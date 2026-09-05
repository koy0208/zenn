#!/usr/bin/env bash
#
# 演習を初期状態（6 個のエラーが仕込まれた状態）に戻す。
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"

# 壊れたモデルを収録しているコミット（引数で上書きできる）
BASELINE="${1:-loop-baseline}"

# パスは -C で移動した先（= $ROOT）からの相対
git -C "$ROOT" checkout "$BASELINE" -- \
    jaffle-shop/models/marts/fct_orders.sql \
    jaffle-shop/models/marts/fct_order_items.sql \
    jaffle-shop/models/marts/dim_customers.sql \
    jaffle-shop/models/staging/stg_orders.sql \
    jaffle-shop/models/staging/stg_products.sql

rm -f "$ROOT/jaffle-shop/dev.duckdb" "$ROOT/jaffle-shop/dev.duckdb.wal"
rm -rf "$ROOT/logs" "$ROOT/jaffle-shop/target"

# ratchet で入れたものを外し、第 1 段階のゲートに戻す
rm -f "$HERE/lint_diff.py"
rm -f "$ROOT/jaffle-shop/data-tests/assert_supply_cost_reconciles.sql"
rm -f "$HERE/contract.sha256"   # 次回の verify.sh で第 1 段階のハッシュが記録される

cat > "$ROOT/LOOP_STATE.md" <<'EOF'
# ループの状態

モデルはセッション間で何も覚えていない。このファイルが覚えている。
1 イテレーションごとに追記する。上書きしない。

## 現在地

- イテレーション: 0（未実行）
- 最後の `verify.sh`: 未実行
- 残っている失敗: 未確認

## 履歴

<!-- ここから下に、新しいイテレーションを上から追記していく -->
EOF

echo "初期状態に戻した。./bin/verify.sh で FAIL を確認できる。"
