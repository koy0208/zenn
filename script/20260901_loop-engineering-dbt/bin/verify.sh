#!/usr/bin/env bash
#
# ループの合格判定ゲート。
#
# ここが「done」の定義そのもの。エージェントはこのスクリプトと
# contract.sha256、および契約ファイル（*.yml / data-tests/*.sql）を
# 書き換えてはならない。書き換えたらこのスクリプトが自分で検知して落ちる。
#
# 終了コード:
#   0 = 全部緑。ループを止めてよい。
#   1 = dbt が落ちた。まだ直す仕事が残っている。
#   2 = 契約が改変された。修正ではなくズルなので、ループを止めて人間を呼ぶ。
#
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
PROJECT="$ROOT/jaffle-shop"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"

STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="$LOG_DIR/verify-$STAMP.log"

# --- 1. 契約の改ざん検知 -------------------------------------------------
# テストを消す・ゆるめる、という「通ったことにする」修正を機械的に禁じる。
contract_files() {
    find "$PROJECT/models" -name '*.yml' -print0
    find "$PROJECT/data-tests" -name '*.sql' -print0
}

current_sum() {
    contract_files | sort -z | xargs -0 shasum -a 256 | shasum -a 256 | awk '{print $1}'
}

EXPECTED_FILE="$HERE/contract.sha256"
ACTUAL="$(current_sum)"

if [[ -f "$EXPECTED_FILE" ]]; then
    EXPECTED="$(cat "$EXPECTED_FILE")"
    if [[ "$ACTUAL" != "$EXPECTED" ]]; then
        {
            echo "=== VERIFY RESULT ==="
            echo "status: CONTRACT_VIOLATION"
            echo "detail: テスト定義（*.yml / data-tests）が変更されている"
            echo "expected_sha256: $EXPECTED"
            echo "actual_sha256:   $ACTUAL"
            echo "テストを書き換えて通すのは修正ではない。モデル側を直すこと。"
        } | tee "$LOG"
        exit 2
    fi
else
    echo "$ACTUAL" > "$EXPECTED_FILE"
    echo "契約のハッシュを記録した: $ACTUAL"
fi

# --- 2. dbt build --------------------------------------------------------
DBT=(uv run --project "$ROOT" dbt)

# duckdb のファイルは profiles.yml の相対パスを cwd 基準で解決する。
# 呼び出し場所によって DB が散らばらないよう、プロジェクト直下に固定する。
cd "$PROJECT" || exit 1

# seeds は先に流す。スキーマが未作成のまま同一 run でモデルを compile すると
# duckdb 側から raw スキーマが見えないため。seed のログは別ファイルに逃がして
# 失敗の詳細が二重に出ないようにする。
"${DBT[@]}" seed --project-dir "$PROJECT" --profiles-dir "$PROJECT" >"$LOG_DIR/seed-$STAMP.log" 2>&1

"${DBT[@]}" build --project-dir "$PROJECT" --profiles-dir "$PROJECT" >"$LOG" 2>&1
DBT_STATUS=$?

# --- 3. 機械可読なサマリ -------------------------------------------------
SUMMARY="$(grep -E '^.*Done\. PASS=' "$LOG" | tail -1 | sed 's/\x1b\[[0-9;]*m//g')"

echo "=== VERIFY RESULT ==="
if [[ $DBT_STATUS -eq 0 ]]; then
    echo "status: PASS"
    echo "${SUMMARY:-Done.}"
    echo "log: $LOG"
    exit 0
fi

echo "status: FAIL"
echo "${SUMMARY:-（サマリ行なし: パースエラーの可能性）}"
echo "log: $LOG"
echo
echo "--- 失敗の詳細 ---"
# パースエラーとモデル/テストの失敗、両方を拾う
DETAIL="$(sed 's/\x1b\[[0-9;]*m//g' "$LOG" \
    | grep -A 4 -E 'Failure in (model|test|seed)|Compilation Error|Runtime Error|Database Error' \
    | head -80)"

if [[ -n "$DETAIL" ]]; then
    echo "$DETAIL"
else
    # dbt までたどり着かなかった場合（依存解決の失敗など）はログ末尾を出す
    sed 's/\x1b\[[0-9;]*m//g' "$LOG" | tail -30
fi
exit 1
