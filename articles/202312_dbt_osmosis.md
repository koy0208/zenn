---
title: "dbt-osmosisをつかって、メタデータ管理を楽にする"
emoji: "📚"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: [dbt,datacatalog]
published: true
---

## はじめに
`dbt`では、各種モデルのメタデータをyamlファイルで管理できます。一方で、依存関係の多いデータモデリングの世界では、すべてのモデルのメタデータを手作業で管理するには限界があります。
例えば、上流のモデルのメタデータが変更された場合（列の定義など）は、そのモデルを継承するモデルのすべてのメタデータを同時に更新する必要があり、かなりの運用コストになるのは想像にかたくないです。

今回は、そんなdbtのyaml管理を楽にしてくれる`dbt-osmosis`を使用して、どこまで運用コストが削減できるかためしてみます。

## 事前準備
大本の実行dbtプロジェクトは、チュートリアルである`jaffle_shop`レポジトリを使用します。事前準備として、各種モデルをDWH上に作成しおきます。（ローカルでも、BigqueryでもなんでもOKです。）

https://github.com/dbt-labs/jaffle_shop

パッケージは、pipでインストールします。
```zsh
pip install dbt-osmosis
```

続いて、プロジェクトファイルに`dbt-osmosis`の設定を追加します。追加するのは、`+dbt-osmosis: "{yaml名}.yml"`のみです。モデルごとにyamlファイルを作成する（`{model}.yml`とする）こともできますし、すでにyamlファイルが存在する場合は名前をあわせます。（今回は`schema.yml`）
また、フォルダごとに異なった名前でyamlファイルを管理している場合もなどでも柔軟に設定できます。
設定はこれだけです！
```yml:dbt_project.yml
models:
  jaffle_shop:
      +dbt-osmosis: "schema.yml"
      materialized: table
      staging:
        materialized: view
        +dbt-osmosis: "schema.yml"
```

## 実行
さて、いきなりですが実行して、yamlファイルを確認してみます。（左が実行前、右が実行後です）
```zsh
dbt-osmosis yaml refactor
```

実行によって、以下が自動で行われます。

- descriptionの追加
- 列型の追加
- 列の追加
- 列順の並び替え（DWH上のテーブルにあわせる）


実行前後の比較
![Alt text](/images/202312_dbt_osmosis/image.png)

![Alt text](/images/202312_dbt_osmosis/image-1.png)


ここで注意点ですが、**yamlファイルには最低限modelのnameを追加する**必要があります。試しに、以下のように`schema.yml`から、`customers`に関する部分を削除して、実行すると`KeyError: 'sources'`とエラーがでてきます。
![Alt text](/images/202312_dbt_osmosis/image-2.png)

逆にいうと、modelのnameさえ記載があれば、列名の記載などはテーブルから読み込んで勝手に補完してくれるということですね。
## descriptionの伝播
これだけでも随分と便利なのですが、`dbt-osomosis`の個人的な真価は、列のdescription（以下列description）を伝播させられることです。これは、上流のモデルの列descriptionさえ管理しておけば、列を継承しているすべての下流モデルの列descriptionは、勝手に更新されるということです。

jaffle_shopの例では、`customers`モデルの`customer_id`は、`stg_customers`モデルの`customer_id`を継承してます。まずは、`stg_customers`モデルの`customer_id`のdescriptionのみを記載しておき、先ほど同様に実行します。


すると、上流のdescriptionがしっかりと継承されています。（列名が同一の場合のみ）

`stg_customers`のyamlファイル
![Alt text](/images/202312_dbt_osmosis/image-4.png)

`customers`のyamlファイル
![Alt text](/images/202312_dbt_osmosis/image-5.png)

ただし、もう一度`stg_customers`の列descriptionを更新しても、下流モデルのdescriptionは更新されません。実は、デフォルトで空のdescriptionのみを対象するので、すでに記載がある場合は更新されません。

![Alt text](/images/202312_dbt_osmosis/image-7.png)

以下のようにすれば継承を強制することもできます。（下流モデルに特記したdescriptionがある場合でも、強制的に上書きさされてしまうので注意です！）

```zsh
dbt-osmosis yaml refactor　--force-inheritance
```
![Alt text](/images/202312_dbt_osmosis/image-6.png)

無事に更新されました。

## まとめ
どこをマスターとして列descriptionを管理していくのか？下流モデルの特記事項をどう管理するのか？同名異義の列名をどうするか？など考慮すべき点はいくつかありそうですが、`dbt-osomosis`を使えば、メタデータの運用コストをかなりさげられそうな気がしてきましたね。
メタデータ管理は、運用コストをできるだけ減らして高い品質を担保することが重要なので、積極的に活用していきたいです。


## 参考

https://github.com/z3z1ma/dbt-osmosis
https://www.yasuhisay.info/entry/2023/04/08/151748