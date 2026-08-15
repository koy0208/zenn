---
title: "dbtをつかって、athenaをデータウェアハウス化する"
emoji: "🚀"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: [aws, dbt]
published: true
published_at: 2023-12-26 11:01
---
AWSathenaはS3へ保続されているデータに直接SQLを発行できるサーバレスなサービスです。通常はデータレイクに対するアドホック分析として使用されるathenaですが、今回はdbtと組み合わせて、データウェアハウスのように使えるようにしてみます。

## 事前準備
事前に以下を設定しておきます。
- aws cliの設定
- dbt-athenaのインストール
    ```zsh
    pip install dbt-athena-community
    # バージョンの確認
    dbt --version
    Core:
    - installed: 1.7.4
    - latest:    1.7.4 - Up to date!

    Plugins:
    - athena: 1.7.0 - Ahead of latest version!
    ```
- S3バケットの作成（今回は`jaffle-shop-2312`という名前で作成）
- こちらのチュートリアルレポジトリをcloneする。
  @[card](https://github.com/dbt-labs/jaffle_shop)

## dbtのセットアップ
`profiles.yml`に次の設定を追加します。

```yaml:~/.dbt/profiles.yml
jaffle_shop:
  target: athena
  outputs:
    athena:
      database: awsdatacatalog
      region_name: ap-northeast-1
      s3_data_dir: s3://jaffle-shop-2312/tables
      s3_staging_dir: s3://jaffle-shop-2312/athena_query_result
      s3_data_naming: table
      schema: jaffle_shop
      threads: 1
      type: athena
      aws_profile_name: default
      workgroup: primary
```
いくつかオプショナルな設定はありますが、意味としては以下の通りです。
- database
  - データソースの設定、通常は`awsdatacatalog`でOK
- region_name
  - リージョン
- s3_data_dir
  - athenaのデータを格納するS3パス
- s3_staging_dir
  - クエリ結果やmetadataを格納するS3パス
- s3_data_naming
  - デフォルトでは、S3へは`スキーマ名/テーブル名`となりますが、テーブル名のみにする。（後述します。）
- schema
  - デフォルトのデータベース名
- aws_profile_name
  - awsのプロファイル名
- workgroup
  - ワークグループ名

詳細についてはREADMEを参考にします。

https://github.com/dbt-athena/dbt-athena?tab=readme-ov-file#configuring-your-profile

## 実行
それでは、まずはそのまま実行してみます。
```zsh
dbt seed
dbt run
```

実行結果を見てみましょう。しっかりとathenaエディタにデータが表示されていますね。
![Alt text](/images/202312_dbt_athena/image0.png)

s3にもデータが保存されています。
ここで、`tables`の下の階層は、テーブル名になっていますが、上述の`s3_data_naming`を`schema_table_unique`と指定すると、`tables/データベース名/テーブル名`となります。データベースを切り分けてテーブルを作成する際にはスキーマ名（データベース名）も階層に入れておいたほうがよさそうです。


![Alt text](/images/202312_dbt_athena/image3.png)
![Alt text](/images/202312_dbt_athena/image2.png)


## パーティション設定
S3には、パーティションが設定されていることが多いので、dbtの下流モデルにもパーティションを設定してみます。
`models/orders.sql`に以下の変更を加えます。
- モデル定義の上部に、configを加え、`order_date`をパーティション化するように指定する。
- パーティション列は、テーブルの最後に持ってくる必要があるため、`order_dateの`位置を移動するする。

```diff sql:models/orders.sql
+ {{ config(
+     materialized='table',
+     partitioned_by=['order_date'],
+ ) }}
...
    select
        orders.order_id,
        orders.customer_id,
        orders.status,
-        orders.order_date
        {% for payment_method in payment_methods -%}
        order_payments.{{ payment_method }}_amount,
        {% endfor -%}
        order_payments.total_amount as amount,
+        orders.order_date
    from orders
...
```

![Alt text](/images/202312_dbt_athena/image.png)
![Alt text](/images/202312_dbt_athena/image4.png)

ちゃんとパーティションテーブルになっているようです。

## まとめ
athenaとdbtを使った事例は少ないので、ベストプラクティスをさぐっていきたいです。

## 参考
[dbt-athenaことはじめ](https://qiita.com/n-gondo123/items/34bb07a0b2b5333bdc34)
[Amazon Athenaに対してローカル環境からdbtを使ってみた](https://dev.classmethod.jp/articles/get-start-dbt-core-with-athena/)