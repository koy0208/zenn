# ループの状態

モデルはセッション間で何も覚えていない。このファイルが覚えている。
1 イテレーションごとに追記する。上書きしない。

## 現在地

- イテレーション: 1
- 最後の `verify.sh`: FAIL / PASS=20 ERROR=2 SKIP=27
- 残っている失敗: `stg_orders`（マクロ未定義）、`stg_products`（列参照）

## 履歴

<!-- ここから下に、新しいイテレーションを上から追記していく -->

### イテレーション 1

- **直した失敗**: `Compilation Error: Model 'fct_orders' depends on a node named 'stg_stores' which was not found`
- **原因**: 店舗のステージングモデルは `stg_locations` という名前で存在しているのに、
  `fct_orders` がソース側の呼び名（`stores`）のまま `ref()` していた。
  モデルが無いのではなく、参照名が実体と食い違っていた。
- **変更**: `jaffle-shop/models/marts/fct_orders.sql` の `ref('stg_stores')` → `ref('stg_locations')`
- **監査**: 契約ファイルの差分ゼロ。禁止パターン（distinct / any_value / inner join / is not null）なし。
- **結果**: パースが通り、初めてモデルが実行された。PASS=0 → PASS=20。
- **残り**: 2 件（どちらもステージング層。上流から順に片付く）
