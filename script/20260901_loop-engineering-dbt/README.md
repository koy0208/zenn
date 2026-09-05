# ループエンジニアリングで dbt のエラーを潰すハンズオン

わざと 6 個のエラーを仕込んだ dbt プロジェクトを、
**エージェントに 1 件ずつプロンプトを打って直させるのではなく、
勝手に直り続ける仕組みを設計して**片付ける演習。

元ネタは Addy Osmani の [Loop Engineering](https://addyosmani.com/blog/loop-engineering/)。
そこで挙げられている 5 つの構成要素を、そのまま dbt に対応させてある。

| 構成要素 | この演習での実装 |
| --- | --- |
| Automations | `/loop /fix-next` — `.claude/commands/fix-next.md` |
| Worktrees | `git worktree` でイテレーションを隔離する |
| Skills | `.claude/skills/dbt-loop/SKILL.md` — 粒度・規約・禁止事項 |
| Plugins / Connectors | `bin/verify.sh` が dbt と DuckDB を叩く境界 |
| Sub-agents | `dbt-fixer`（作る）と `dbt-reviewer`（検証する）の分離 |
| State | `LOOP_STATE.md` |

## 準備

必要なのは [uv](https://docs.astral.sh/uv/) だけ。dbt も DuckDB も uv が入れる。

```sh
cd script/20260901_loop-engineering-dbt
uv sync
```

## まず壊れていることを確認する

```sh
./bin/verify.sh
```

`status: FAIL` と、いちばん上流のエラーが出れば準備完了。

```
=== VERIFY RESULT ===
status: FAIL
--- 失敗の詳細 ---
Compilation Error
  Model 'model.jaffle_shop.fct_orders' (models/marts/fct_orders.sql) depends on a node named 'stg_stores' which was not found
```

## ループを回す

```sh
claude
```

を起動して、

```
/loop /fix-next
```

`verify.sh` が `status: PASS` を返すまで、
「失敗を 1 件選ぶ → `dbt-fixer` が直す → `dbt-reviewer` が監査する → `LOOP_STATE.md` に記録する → コミットする」
が繰り返される。

並行して他の作業をするなら worktree で隔離する。

```sh
git worktree add ../loop-run -b loop-run
```

## 仕込んであるエラー

前半 4 つは構文の問題で、機械的に直せる。
**後半 2 つは構文としては正しく、意味が壊れている。**
ここでループの限界が出る。

| # | 症状 | 種類 |
| --- | --- | --- |
| 1 | `depends on a node named 'stg_stores' which was not found` | コンパイルエラー |
| 2 | `'cents_to_dollar' is undefined` | コンパイルエラー |
| 3 | `Column "product_price" ... cannot be referenced before it is defined` | 実行時エラー |
| 4 | `column "location_id" must appear in the GROUP BY clause` | 実行時エラー |
| 5 | `unique_fct_order_items_order_item_id: Got 5795 results` | テスト失敗 |
| 6 | `not_null_dim_customers_count_lifetime_orders: Got 181 results` | テスト失敗 |

4 番のエラーメッセージは DuckDB が親切に `any_value()` を提案してくる。
それに従うと**テストは緑になるが、モデルは壊れたまま**になる。
5 番も `distinct` を足せば `unique` テストだけは通る。

こうした「通ったことにする」直し方を防ぐのがループ側の仕事で、初期状態では 3 段構えにしてある。

1. `verify.sh` がテスト定義のハッシュを持っていて、書き換えを終了コード 2 で弾く
2. `data-tests/assert_*_grain.sql` が行数を突き合わせるので、行を捨てる修正も落ちる
3. `dbt-reviewer` が `git diff` を読んで、禁止された直し方を差し戻す

**3 段あってなお、`qualify` は 1 と 2 をすり抜ける。** 止まるのは 3 だけ。
つまり LLM の判断が最後の砦になっている。ここが次の話につながる。

## 第 2 段階：ゲートを締める（ratchet）

4 周目で「テストは全部緑なのに値が 40 倍ズレている」を体験したら、実行する。

```sh
./bin/ratchet.sh
./bin/verify.sh   # 新しい契約ハッシュが記録される
```

入るのは 2 つ。どちらも **LLM の判断を機械に置き換える**ためのもの。

| 追加されるもの | 効き方 |
| --- | --- |
| `data-tests/assert_supply_cost_reconciles.sql` | 形ではなく《値》を、モデルの計算経路を通らずにソースから組み直して突き合わせる |
| `bin/lint_diff.py` | `distinct` / `qualify` / `any_value` / `inner join` / `where is not null` を git diff の追加行から検出し、終了コード 3 |

リンタは「常に間違い」とは言わない。該当行に `loop-ok: <理由>` と書けば通る。
**黙って通ることはできない**という形にして、ショートカットを《記録された判断》に変えるのが狙い。

同じショートカットをもう一度当てると、今度はこうなる。

```
=== VERIFY RESULT ===
status: NEEDS_JUSTIFICATION
  jaffle-shop/models/marts/fct_order_items.sql:43  [qualify]
    → row_number() で 1 行に絞ると、残った行以外の値が捨てられる。

# loop-ok を書いてリンタを迂回しても、今度は値のテストが落ちる
Failure in test assert_supply_cost_reconciles
  Got 10 results, configured to fail if != 0
```

これが答え。**監査役が手で数えたことを、その場でテストに昇格させる。**
ゲートは一方向にしか動かない ─ ゆるめるのは契約違反、締めるのは人間の仕事。

## 答え合わせ

```sh
# ループが出した差分
git diff loop-baseline -- jaffle-shop/models > /tmp/mine.diff

# 想定解と読み比べる
diff /tmp/mine.diff solution/reference-fix.diff
```

`solution/` には 2 つ置いてある。

- `reference-fix.diff` — 想定解の差分
- `LOOP_STATE.completed.md` — 実際に 6 イテレーション回したときの記録。
  **却下された修正とその理由**も残してある

読み比べるときは、違っていた箇所より
**同じでも理由を説明できない箇所**を探すこと。そこが理解の負債になる。

## やり直す

```sh
./bin/reset.sh
```

モデルを初期状態に戻し、`LOOP_STATE.md`・DuckDB・ログを消す。
契約ファイル（`*.yml` と `data-tests/`）は演習中も変わらないので触らない。
