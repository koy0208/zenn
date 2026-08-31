# ループの状態

モデルはセッション間で何も覚えていない。このファイルが覚えている。
1 イテレーションごとに追記する。上書きしない。

## 現在地

- イテレーション: 2
- 最後の `verify.sh`: FAIL / PASS=27 ERROR=1 SKIP=21
- 残っている失敗: `stg_products`（列参照）

## 履歴

<!-- ここから下に、新しいイテレーションを上から追記していく -->

### イテレーション 2

- **直した失敗**: `Compilation Error in model stg_orders: 'cents_to_dollar' is undefined`
- **原因**: マクロ名の単複の打ち間違い。定義は `cents_to_dollars`（複数形）で、
  同じファイル内の `tax_paid` と `order_total` は正しく複数形で呼べていた。
  `subtotal` の 1 行だけが単数形だった。
- **変更**: `jaffle-shop/models/staging/stg_orders.sql` の `cents_to_dollar('subtotal')` → `cents_to_dollars('subtotal')`
- **監査**: 契約ファイルの差分ゼロ。禁止パターンなし。
  マクロ側を単数形に合わせて定義し直す手もあるが、それだと他の 2 箇所が壊れるので却下。
- **結果**: PASS=20 → PASS=27
- **残り**: 1 件

### イテレーション 1

- **直した失敗**: `Compilation Error: Model 'fct_orders' depends on a node named 'stg_stores' which was not found`
- **原因**: 店舗のステージングモデルは `stg_locations` という名前で存在しているのに、
  `fct_orders` がソース側の呼び名（`stores`）のまま `ref()` していた。
  モデルが無いのではなく、参照名が実体と食い違っていた。
- **変更**: `jaffle-shop/models/marts/fct_orders.sql` の `ref('stg_stores')` → `ref('stg_locations')`
- **監査**: 契約ファイルの差分ゼロ。禁止パターン（distinct / any_value / inner join / is not null）なし。
- **結果**: パースが通り、初めてモデルが実行された。PASS=0 → PASS=20。
- **残り**: 2 件（どちらもステージング層。上流から順に片付く）
