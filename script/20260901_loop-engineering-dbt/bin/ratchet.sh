#!/usr/bin/env bash
#
# ゲートを一段締める（ratchet）。
#
# 4 周目で「テストは全部緑なのに値が 40 倍ズレている」を体験したあとに実行する。
# 監査役が手で数えたことを、機械が毎回数えるように昇格させるのがこのスクリプト。
#
# 入るもの:
#   1. data-tests/assert_supply_cost_reconciles.sql
#        形（行数・主キー）ではなく《値》をソースから独立に組み直して突き合わせる。
#   2. bin/lint_diff.py
#        distinct / qualify / any_value / inner join / where is not null を
#        git diff の追加行から機械的に検出する。終了コード 3。
#
# 契約ハッシュも一緒に更新する。ratchet は人間の仕事であって、
# ループが自分でゲートをゆるめられないのと同様、自分で締めることもしない。
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"

cp "$ROOT/ratchet/assert_supply_cost_reconciles.sql" "$ROOT/jaffle-shop/data-tests/"
cp "$ROOT/ratchet/lint_diff.py" "$HERE/"

rm -f "$HERE/contract.sha256"

echo "ゲートを締めた:"
echo "  + jaffle-shop/data-tests/assert_supply_cost_reconciles.sql（値の照合）"
echo "  + bin/lint_diff.py（差分リンタ / exit 3）"
echo
echo "次に ./bin/verify.sh を実行すると、新しい契約ハッシュが記録される。"
echo "同じショートカットをもう一度当てて、今度は止まることを確かめること。"
