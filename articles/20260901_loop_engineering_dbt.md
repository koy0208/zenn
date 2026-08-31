---
title: "dbtのエラーを1件ずつ直すのをやめる ─ ループエンジニアリングの実践"
emoji: "🔁"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: [dbt, claudecode, duckdb, dataengineering, ai]
published: false
---

## はじめに

皆さんこんにちは！アナリティクスエンジニアの山本です。

dbt を触っていると、`dbt build` が真っ赤になっている朝があります。
コンパイルエラーを直すと実行時エラーが出て、それを直すとテストが落ちる。
1 件直しては再実行し、次のエラーをコピーしてまた AI に投げる。
この「エラーをコピペしてプロンプトを打つ」作業を、そろそろやめたい。

Addy Osmani が [Loop Engineering](https://addyosmani.com/blog/loop-engineering/) で書いているのは、まさにそこの話です。

> I don't prompt Claude anymore. I have loops running that prompt Claude.

エージェントにプロンプトを打つ人の役割を、自分で仕組みに置き換える。
この記事では、それを **わざと 6 個のエラーを仕込んだ dbt プロジェクト** で実際にやってみます。

そして結論から言うと、**ループは 6 個中 4 個を気持ちよく片付け、残り 2 個で盛大に騙されました。**
その騙され方のほうが本題です。

## 30秒まとめ

- Why（なぜやるか）
  - dbt のエラー対応は「実行 → エラーを読む → 直す → 再実行」の繰り返しで、構造がいつも同じ。
    毎回プロンプトを打つのは、同じループを人間が手回ししているだけ。

- What（なにをやるか）
  - Addy Osmani の 5 要素（Automations / Worktrees / Skills / Connectors / Sub-agents）＋ State を、dbt プロジェクトに実装する。

- How（どうやるか）
  - 合格条件を `verify.sh` という 1 本のスクリプトに落とし、終了コードでループの停止条件にする。
  - プロジェクトの粒度・規約・**禁止された直し方**を Skill に書き出す。
  - 実装するエージェントと検証するエージェントを分ける。
  - 進捗を `LOOP_STATE.md` に残す。モデルは忘れるが、リポジトリは忘れない。

:::message
ハンズオン一式はリポジトリに置いてあります。uv さえ入っていれば動きます。
`script/20260901_loop-engineering-dbt/`
:::

## プロンプトエンジニアリングとの違い

1 年前のやり方はこうでした。

1. 良いプロンプトを書く
2. 出力を読む
3. 次のプロンプトを打つ

エージェントは道具で、ターンを回すのは常に人間です。
Addy はこれを "holding it the entire time, one turn after the other" と表現しています。

ループエンジニアリングでは、**仕事を見つけ、割り振り、検証し、記録し、次を決める小さなシステム**を作ります。
設計は一度きりで、あとは勝手に回ります。

元記事の 5 要素を、今回の dbt プロジェクトにそのまま対応させました。

| 構成要素 | 役割 | この演習での実装 |
| --- | --- | --- |
| Automations | ループの心臓部 | `/loop /fix-next` |
| Worktrees | 並列作業を衝突させない | `git worktree` |
| Skills | プロジェクトを毎回説明しなくて済むようにする | `.claude/skills/dbt-loop/SKILL.md` |
| Connectors | 実際のツールに触る境界 | `bin/verify.sh`（dbt と DuckDB） |
| Sub-agents | 作る人と検査する人を分ける | `dbt-fixer` と `dbt-reviewer` |
| State | セッションをまたいで覚えておく | `LOOP_STATE.md` |

## 題材：わざと壊した dbt プロジェクト

dbt-labs の `jaffle-shop` を DuckDB 用に組み直し、エラーを 6 個仕込みました。
顧客 935 人、注文 4,000 件、注文明細 5,795 行。モデル 9 本、テスト 34 本です。

仕込んだエラーは、**手前 4 つが構文の問題、後ろ 2 つが意味の問題**という構成にしてあります。

| # | 症状 | 種類 |
| --- | --- | --- |
| 1 | `depends on a node named 'stg_stores' which was not found` | コンパイルエラー |
| 2 | `'cents_to_dollar' is undefined` | コンパイルエラー |
| 3 | `Column "product_price" ... cannot be referenced before it is defined` | 実行時エラー |
| 4 | `column "location_id" must appear in the GROUP BY clause` | 実行時エラー |
| 5 | `unique_fct_order_items_order_item_id: Got 5795 results` | テスト失敗 |
| 6 | `not_null_dim_customers_count_lifetime_orders: Got 181 results` | テスト失敗 |

1〜4 は SQL として壊れているので、機械が読めば直せます。
5〜6 は **SQL としては完全に正しく、意味だけが壊れている**。ここが分水嶺です。

## ループを組む

### 1. 「終わった」を機械が判定できる形にする

ループで最初に決めるのは、プロンプトではなく **停止条件** です。
`bin/verify.sh` がそれを担います。

```sh
$ ./bin/verify.sh
=== VERIFY RESULT ===
status: FAIL
--- 失敗の詳細 ---
Compilation Error
  Model 'model.jaffle_shop.fct_orders' (models/marts/fct_orders.sql) depends on a node named 'stg_stores' which was not found
```

終了コードが判定のすべてです。

| 終了コード | 意味 | 次にやること |
| --- | --- | --- |
| 0 | 全モデル・全テストが緑 | ループを終了する |
| 1 | dbt が落ちた | 失敗を 1 件ずつ直す |
| 2 | 契約が改変された | **停止して人間を呼ぶ** |

3 番目が肝です。
赤を緑にする最短ルートは、いつだって **テストを消すこと** だからです。
`verify.sh` はテスト定義のハッシュを持っていて、書き換えを機械的に検知します。

```bash
contract_files() {
    find "$PROJECT/models" -name '*.yml' -print0
    find "$PROJECT/data-tests" -name '*.sql' -print0
}

current_sum() {
    contract_files | sort -z | xargs -0 shasum -a 256 | shasum -a 256 | awk '{print $1}'
}
```

試しに `unique` テストを 1 行コメントアウトしてみると、こうなります。

```
=== VERIFY RESULT ===
status: CONTRACT_VIOLATION
detail: テスト定義（*.yml / data-tests）が変更されている
expected_sha256: c788623f7134ddcbbb31123bdd8945b07c16c5edffcdbf12bca2afecd11808dc
actual_sha256:   d74604b1219b448181cde7ae3ab136dd2eccec67870d1d1ac7389821198060cf
テストを書き換えて通すのは修正ではない。モデル側を直すこと。
```

**エージェントが採点基準そのものを書き換えられる状態でループを回してはいけません。**

### 2. プロジェクトの前提を書き出す（Skill）

Addy の表現を借りると、Skill は "stop re-explaining your project every single time like a goldfish" のためのものです。

`SKILL.md` には、そのプロジェクトでしか通用しない前提を書きます。今回は 3 つ。

**粒度の表**。これが仕様そのものです。

```markdown
| モデル | 粒度 | 主キー |
| --- | --- | --- |
| `fct_order_items` | 1 行 = 注文明細 1 行 | `order_item_id` |
| `dim_customers` | 1 行 = 1 顧客 | `customer_id` |
```

**規約**。

```markdown
- 金額カラムはセント単位で入ってくる。必ず `{{ cents_to_dollars('col') }}` を通す。
- 1 対多の関係を join するときは、join する前に多側を粒度まで畳む。
- 左外部結合で NULL になりうる集計値は `coalesce(..., 0)` で埋める。
```

そして **やってはいけない直し方**。ここがいちばん効きました。

```markdown
1. テストを消す・ゆるめる
2. `distinct` で重複を潰す
3. `any_value()` で GROUP BY エラーを黙らせる
4. NULL を消すために `inner join` に変える
5. `where ... is not null` で失敗行を除外する
```

これらは全部「赤を緑にする」という意味では成功します。
だからこそ、明示的に禁止しておかないと通ってしまいます。

### 3. 作る役と検証する役を分ける

Addy が "keep the maker away from the checker" と書いている部分です。
コードを書いた本人は、自分の仕事を甘く採点します。

そこでエージェントを 2 つに割りました。

```markdown
---
name: dbt-fixer
description: dbt の失敗を 1 件だけ直す実装役
tools: Read, Edit, Write, Bash, Grep, Glob, Skill
---
自分の修正が正しいかどうかの判断は下さない。それは別のエージェントの仕事。
```

```markdown
---
name: dbt-reviewer
description: 修正が「本当に直っているか」を検証する監査役
tools: Read, Bash, Grep, Glob, Skill
---
あなたは監査役であり、実装者ではない。ファイルを書き換えてはならない。

`verify.sh` が緑なのは、失敗が報告されなくなったという事実にすぎない。
それはモデルが正しいことの証明ではない。あなたはその差を埋めるためにいる。
```

`dbt-reviewer` には `Edit` も `Write` も渡していません。
**権限で役割を強制する**のがポイントです。プロンプトでのお願いは破られます。

### 4. 状態をディスクに置く

モデルはセッションをまたぐと何も覚えていませんが、リポジトリは覚えています。
`LOOP_STATE.md` に 1 イテレーションずつ追記していきます。

書くのは「何を直したか」ではなく **「なぜそうなっていたか」** です。

### 5. 心臓部

ここまで揃えて、ようやくループを回します。

```
/loop /fix-next
```

`.claude/commands/fix-next.md` が 1 イテレーション分の手順です。

```markdown
1. `LOOP_STATE.md` を読み、前回どこまで進んだかを確認する
2. `./bin/verify.sh` を実行する
   - PASS ならループを終了する
   - CONTRACT_VIOLATION なら直ちに停止して人間を呼ぶ
3. 失敗が複数あるときは、最も上流のものを 1 件だけ選ぶ
4. `dbt-fixer` に直させる
5. `dbt-reviewer` に `git diff` を監査させる
6. `LOOP_STATE.md` に記録する
7. コミットする
```

**失敗は 1 件ずつ直します。** まとめて直すと、何がどれを解決したのか分からなくなります。
コンパイルエラー → 実行時エラー → テスト失敗の順に、層が剥がれるように片付きます。

## 実際に回してみる

:::message
以下に載せている `verify.sh` の出力・PASS 件数・DuckDB のクエリ結果は、
すべて実際に実行したものです。イテレーションの手順は `fix-next.md` の定義どおりに進めました。
:::

### イテレーション 1〜3：機械的に片付く

```
イテレーション 1: PASS=0  → PASS=20   ref('stg_stores') → ref('stg_locations')
イテレーション 2: PASS=20 → PASS=27   cents_to_dollar → cents_to_dollars
イテレーション 3: PASS=27 → PASS=36   cents_to_dollars('product_price') → ('price')
```

ここは面白いところが何もありません。エラーメッセージに答えが書いてあるからです。

強いて言えば 3 番目が少しだけ考えます。

```
Binder Error: Column "product_price" referenced that exists in the SELECT clause
  - but this column cannot be referenced before it is defined
```

`product_price` はソースの列名ではなく、**このモデルが付けている出力側の別名** でした。
出力名を入力として読もうとしていたわけです。ソースの実際の列名は `price` です。

3 回目で構文エラーが尽きます。ここから性質が変わります。

### イテレーション 4：ゲートが完全に騙される

残った失敗はこれです。

```
Failure in test unique_fct_order_items_order_item_id
  Got 5795 results, configured to fail if != 0

Failure in test assert_fct_order_items_grain
  Got 1 result, configured to fail if != 0
```

原因は join のファンアウトです。
`stg_supplies` は「SKU ごとの副資材 1 種」が 1 行で、1 SKU あたり 4〜9 行あります。
それを明細に直接 join したので、明細 1 行が副資材の数だけ複製されました。

ここで **重複を消しにいく** と、こうなります。

```sql
select * from joined
qualify row_number() over (partition by order_item_id order by supply_cost) = 1
```

結果を見てください。

```
=== VERIFY RESULT ===
status: FAIL
Done. PASS=43 WARN=0 ERROR=1 SKIP=5 NO-OP=0 TOTAL=49
```

`unique` も粒度テストも **通りました**。残る 1 件は次のバグ（`dim_customers`）です。
行数を数えても正しい。

```
fct rows / distinct keys: (5795, 5795)
stg rows: (5795,)
```

行数 5,795、主キーも一意。テストで検知できる要素は、すべて正しい。

では中身はどうか。

```
ショートカット版が入れた supply_cost
   ('BEV-001', 0.04)
   ('BEV-002', 0.04)
   ('BEV-003', 0.04)
   ('BEV-004', 0.04)
   ('BEV-005', 0.04)

本来あるべき合計値
   ('BEV-001', 0.82)
   ('BEV-002', 1.75)
   ('BEV-003', 1.54)
   ('BEV-004', 0.82)
   ('BEV-005', 0.63)
```

`order by supply_cost` が最安の副資材 1 行だけを残していました。
全 SKU の原価が `0.04` に化けている。**15〜40 倍のズレが、緑のまま通っていた。**

しかもこの `supply_cost` は下流の `fct_orders.order_cost` の材料です。
原価指標が丸ごと壊れた状態で、パイプラインは正常に見えます。

正しい修正は、join する前に多側を畳むことです。

```sql
supply_cost_per_product as (
    -- 副資材は SKU ごとに複数行ある。join してから畳むのでは遅い（行が増えてしまう）。
    select
        product_id,
        sum(supply_cost) as supply_cost
    from {{ ref('stg_supplies') }}
    group by product_id
),
```

そして重要なのは、**ゲートから見ると両者はまったく同じ結果**だということです。

```
ショートカット版: PASS=43 ERROR=1
正しい修正:       PASS=43 ERROR=1
```

区別できたのは、`dbt-reviewer` が値を数えたからです。

> `supply_cost` を `stg_supplies` の SKU 別合計と突き合わせて不一致 0 件を確認。

「テストが通ったので問題ない」という報告を許さない、という 1 行を Skill に書いておいたことが効きました。

### イテレーション 5：エラーメッセージ自身が罠を勧めてくる

```
Binder Error: column "location_id" must appear in the GROUP BY clause
  or must be part of an aggregate function.
  Either add it to the GROUP BY list, or use "ANY_VALUE(location_id)"
  if the exact value of "location_id" is not important.
```

DuckDB が親切に `ANY_VALUE()` を提案してきます。従うと通ります（PASS=47）。

しかも今回のデータでは、**`any_value` の結果はたまたま正しい**。
このデータセットでは 935 人全員が 1 店舗にしか紐づいていないからです。

それでも却下しました。理由は 2 つあります。

1. `location_id` は下流の `joined` で一度も参照されていません。
   誰も読まない列を、集計してまで残す理由がない。
2. 「顧客は 1 店舗にしか紐づかない」という不変条件は、
   モデルにもテストにも **どこにも書かれていません**。
   顧客が 2 店舗目で注文した日に、エラーも出さずに壊れます。

正しい修正は、その行を消すことでした。

エラーメッセージが教えてくれるのは **黙らせ方** であって、直し方ではありません。

### イテレーション 6：完了

```
Failure in test not_null_dim_customers_count_lifetime_orders
  Got 181 results
```

935 人のうち 181 人は、この期間に注文がありません。
`left join` なので集計側が当たらず NULL になります。

データの欠損ではなく、**「注文回数 0」を NULL で表現してしまっていた** のが原因です。

```sql
coalesce(customer_orders.count_lifetime_orders, 0) as count_lifetime_orders,
coalesce(customer_orders.lifetime_spend, 0) as lifetime_spend,
```

`inner join` に変える案もありますが、181 行が消えて粒度テストが落ちます。
仕様（1 行 = 1 顧客、注文がなくても残す）にも反します。

```
=== VERIFY RESULT ===
status: PASS
Done. PASS=49 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=49
```

ループ終了です。6 イテレーション、コミット 6 本。

## ループが解決してくれない 3 つのこと

Addy は元記事の最後に、"Loop gets better ≠ Problems get easier" と書いています。
むしろ 3 つの問題は鋭くなる、と。今回の演習でも、そのまま起きました。

### 1. Verification（検証）

> "its done" is a claim and not a proof

イテレーション 4 がまさにこれでした。
テストは全部緑、行数も主キーも正しい。それでも値は 15〜40 倍ズレていた。

**テストが通ったことと、モデルが正しいことは別物です。**
そして自動化されたゲートは、前者しか判定できません。

この差を埋めるために今回やったのは 3 段構えです。

1. `verify.sh` がテスト定義のハッシュを持ち、書き換えを終了コード 2 で弾く
2. `data-tests/assert_*_grain.sql` が行数を突き合わせ、行を捨てる修正を落とす
3. `dbt-reviewer` が `git diff` を読み、禁止された直し方を差し戻す

3 段あってなお、`qualify` は 1 と 2 をすり抜けました。止めたのは 3 だけです。

### 2. Comprehension Debt（理解の負債）

ループが速くコードを出すほど、**実装内容と自分の理解の差が開いていきます。**

今回は 6 イテレーションで 5 ファイルしか変わっていないので、まだ全部読めます。
でも、これが 50 イテレーション・30 ファイルだったら？

対策として `LOOP_STATE.md` には「症状ではなく原因を書く」ことを義務づけました。
さらに終了時には、**テストで担保されていないことの申し送り** を書かせています。

```markdown
## 終了時の申し送り

ゲートは緑だが、以下はテストで担保されていない。人間が見るべき箇所。

2. `fct_orders.count_order_items` は、明細のない注文 27 件で NULL になる。
   現在テストがないため緑のまま通っている。これが仕様どおりかは未確認。
3. `supply_cost` は「SKU 1 個あたりの副資材コスト合計」。
   明細の数量という概念がまだモデルに無いので、注文単位の原価は数量を無視している。
```

緑で終わったループが、自分で「ここは見ていない」と申告する。
これがないと、PASS=49 という数字だけが残ります。

### 3. Cognitive Surrender（認知的降伏）

いちばん危ないのは、ループが回っていることに安心して、意見を持つのをやめることです。

> the comfortable posture is the dangerous one

`PASS=49 / ERROR=0` は気持ちいい数字です。
でも、その 49 のうち何本が本当に意味のあるテストなのかは、誰も保証していません。

今回、`fct_orders.count_order_items` に `not_null` を張っていたら、
明細のない注文 27 件で落ちていたはずです。張らなかったから緑でした。
**テストがない場所は、常に緑です。**

## まとめ

- dbt のエラー対応は構造がいつも同じなので、ループにする価値がある。
- ループを組むときに最初に決めるのはプロンプトではなく **停止条件**。
  `verify.sh` の終了コードがそれ。
- **エージェントが採点基準を書き換えられる状態にしない。** 契約はハッシュで固定する。
- プロジェクト固有の前提（粒度・規約・**やってはいけない直し方**）は Skill に書き出す。
- 作る役と検証する役を分け、検証役からは書き込み権限を取り上げる。
- 構文エラーはループが片付ける。**意味のエラーで人間の判断が要る。**
  そしてゲートは、その 2 つを区別できない。

レバレッジの効く場所が、プロンプトを書くことからループを設計することに移った、というのが元記事の主張です。
やってみて思うのは、**ループ設計のほうが難しい**ということでした。
「何をもって完了とするか」を先に言語化しないと、そもそも書けないからです。

## 参考

https://addyosmani.com/blog/loop-engineering/

https://docs.getdbt.com/docs/build/data-tests

https://github.com/dbt-labs/jaffle-shop
