# ループの状態

モデルはセッション間で何も覚えていない。このファイルが覚えている。
1 イテレーションごとに追記する。上書きしない。

## 現在地

- イテレーション: 3
- 最後の `verify.sh`: FAIL / PASS=36 ERROR=2 SKIP=11
- 残っている失敗: `fct_order_items` の `unique` テストと粒度テスト（構文ではなく意味の問題）

## 履歴

<!-- ここから下に、新しいイテレーションを上から追記していく -->

### イテレーション 3

- **直した失敗**: `Binder Error in stg_products: Column "product_price" referenced that exists in the SELECT clause - but this column cannot be referenced before it is defined`
- **原因**: ソース `raw_products` の列名は `price` で、`product_price` は
  このモデルが付ける**出力側**の別名だった。出力名を入力として読もうとしていた。
- **変更**: `jaffle-shop/models/staging/stg_products.sql` の `cents_to_dollars('product_price')` → `cents_to_dollars('price')`
- **監査**: 契約ファイルの差分ゼロ。`raw_products.csv` のヘッダが `sku,name,type,price,description` であることを確認。
- **結果**: PASS=27 → PASS=36。**構文エラーはこれで尽きた。**
- **残り**: 2 件。どちらも SQL としては正しく走った上でのテスト失敗。ここから性質が変わる。

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
