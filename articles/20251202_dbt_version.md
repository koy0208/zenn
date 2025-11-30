---
title: "dbtのバージョン管理"
emoji: "🔄"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: [dbt]
published: false
---

この記事は、[ナウキャストAdventCalendar2025](https://qiita.com/advent-calendar/2025/nowcast)の2日目の記事です。

## はじめに
皆さんこんにちは！ナウキャストアナリティクスエンジニアの山本です。

突然ですが、皆さんdbtって好きですか？好きですよね？
ナウキャストでは、snowflake×dbtを中心にデータ基盤が構築されており、各種プロダクトからデータが呼び出されています。
今回は、プロダクトから参照されるデータモデルに必要不可欠な「データモデルのバージョン管理」の話を書いていきます。

## 30秒まとめ
-  Why（なぜやるか）
   -  プロダクトから参照されるデータモデルについて、安心安全に開発したい。

- What（なにをやるか）
  - dbtのバージョン管理を活用し、モデルの開発とプロダクトの開発を切り離す。

- How（どうやるか）
  - yamlファイルでモデルのバージョンを管理する。
  - モデルが破壊的に変更される場合、中身が大きく変わる場合は、モデルの別バージョンを作成する。
  - 最新バージョンを参照するviewを使用することで、プロダクト側は変更を加えず新モデルをリリースできる。

## データモデルとプロダクト
ナウキャストでは、複数のデータホルダーからデータを集め、各種クライアントへプロダクトとして提供しています。

![alt text](/images/20251202/image.png)

特に、私が所属するREU（Real Estate Unit）では、不動産業界のクライアントへ向けたSaaSアプリケーションを提供しており、snowflake上のデータを直接参照する仕組みになっています。
つまり、データモデルの品質や安定性がそのままクライアント体験に直結するのが特徴です。そのため、既存モデルをそのまま書き換えると、当然ながらプロダクト側は影響を受けてしまいます。

- データモデルは、最新のアップデートにあわせてどんどん開発したい。
- プロダクト側は顧客影響を加味して慎重に開発したい。

この二つを両立するために役立つのが**dbtのバージョン管理**です。

## dbtモデルのバージョン管理
さて、ここからが本題です。dbtにはyamlで、モデルのバージョン管理ができる便利な機能があります。`jaffle_shop`のサンプルデータで実際にやってみます。

https://docs.getdbt.com/docs/mesh/govern/model-versions

https://github.com/dbt-labs/jaffle-shop/tree/main


### サンプルモデル
例えば、顧客の属性情報を管理するテーブル`dim_customers`を想定し、v1とv2モデルを作成します。
年齢ごとに区分を作成する加工を入れており、v1とv2では区分が異なります。さらに、v2では顧客名を削除しています。

プロダクト側でv1のモデルを使用していた場合、v2でロジックをそのままv1を更新すると、当然エラーが起こります。
（カラムも減っているし、年齢区分も変化している。）

```sql:dim_customers_v1.sql

with src as (
select 
    customer_id,
    customer_name,
    floor(random() * 60) + 20 as age
from {{ ref('stg_customers') }}
)
select 
    customer_id,
    customer_name,
    age,
    case
        when age < 30 then 'Young Adult'
        when age between 30 and 50 then 'Adult'
        else 'Senior'
    end as age_group
from src
```

```sql:dim_customers_v2.sql
with src as (
select 
    customer_id,
    customer_name,
    floor(random() * 60) + 20 as age
from {{ ref('stg_customers') }}
)
select 
    customer_id,
    -- customer_name, -- 顧客名を削除
    age,
    -- 年齢区分がv1と異なる。
    case
        when age < 30 then 'young'
        when age between 30 and 50 then 'middle'
        else 'senior'
    end as age_group
from src

```

### バージョン機能の使い方

バージョン機能を使用するには、model.yamlを書き換えます。

```yml:model.yml
models:
  - name: dim_customers
    versions:
      - v: 1
      - v: 2
    latest_version: 2
```

すると、dbt内部では複数のモデルをSQL内で切り替えることができます。
```sql

-- versionを明示的に指定
select * from {{ ref('dim_customers', v=1) }} limit 10;

-- versionを明示的しなければ、latestが参照される
select * from {{ ref('dim_customers') }} limit 10;
```

dbt内部のモデルであれば、`{{ ref('dim_customers') }}`で常に最新モデルが参照されます。
しかし、プロダクト側でテーブル名を明示している場合は、`dim_customers_v2`とする必要があり、モデルの更新には、テーブル名も書き換えないといけません。

そこで、常に最新バージョンを参照するviewを作成するマクロを使用します。

```sql
{% macro create_latest_version_view() %}

    -- this hook will run only if the model is versioned, and only if it's the latest version
    -- otherwise, it's a no-op
    {% if model.get('version') and model.get('version') == model.get('latest_version') %}

        {% set new_relation = this.incorporate(path={"identifier": model['name']}) %}

        {% set existing_relation = load_relation(new_relation) %}

        {# ここで、view でも table でもあれば一旦 drop する #}
        {% if existing_relation %}
            {{ drop_relation_if_exists(existing_relation) }}
        {% endif %}
        
        {% set create_view_sql -%}
            create view {{ new_relation }} as
            select * from {{ this }}
        {%- endset %}
        
        {% do log("Recreating view " ~ new_relation ~ " pointing to " ~ this, info = true) if execute %}
        
        {{ return(create_view_sql) }}
        
    {% else %}
    
        -- no-op
        select 1 as id
    
    {% endif %}

{% endmacro %}

```

```diff yml:dbt_project.yml
# 上記マクロがbuild時に動作するようにdbt_project設定を加える
models:
  jaffle_shop:
+    post-hook:
+       - "{{ create_latest_version_view() }}"
    staging:
      +materialized: view
    marts:
      +materialized: table

```

実際に実行してみるとこんか感じです。
```zsh
dbt build -s dim_customers # これで、v1もv2を同時に実行

>
00:45:56  4 of 8 START sql table model main.dim_customers_v1 ............................. [RUN]
00:45:56  5 of 8 START sql table model main.dim_customers_v2 ............................. [RUN]
# ここで、v2がdim_customerのviewにマッピングされていることがわかる
00:45:56  Recreating view "dev"."main"."dim_customers" pointing to "dev"."main"."dim_customers_v2"
00:45:56  5 of 8 OK created sql table model main.dim_customers_v2 ........................ [OK in 0.03s]
00:45:56  4 of 8 OK created sql table model main.dim_customers_v1 ........................ [OK in 0.03s]
```

dim_customers（view）は、v2が参照されていることがわかります。

![alt text](/images/20251202/image-0.png)

![alt text](/images/20251202/image-1.png)

![alt text](/images/20251202/image-2.png)


プロダクト側では、常にこのviewを参照するようにしておけば、コードを書き換えることなくデータモデルの開発とリリースを行うことができます！
ちなみに各バージョンごとにテストやカラムの設定を変えることもできるので、モデルごとにデータ品質をチェックできます。

```yml:model.yml
models:
  - name: dim_customers
    columns:
      - name: customer_id
      - name: customer_name
        data_tests:
          - not_null
      - name: age
      - name: age_group
    versions:
      - v: 1
        columns:
          - name: age_group
            data_tests:
              - accepted_values:
                  values: ["Young Adult", "Adult", "Senior"]
      - v: 2
        columns:
          - include: all
            exclude: [customer_name] # exludeで反映しないカラムを設定
          # テストをv1と分離して実行
          - name: age_group
            data_tests:
              - accepted_values:
                  values: ["young", "middle", "senior"]

    latest_version: 2
```

## バージョン管理のメリットとデメリット
モデルバージョン管理のメリットは、破壊的な変更に対して頑健になるということ以外にもいくつかのメリットがあります。

- プロダクト側への反映タイミングと基盤側への反映タイミングをわけることができる。
  - データの中身が大きく変わるとクライアントに不信感を与える可能性がある。
  - データ基盤側には最新モデルを作成しておき、クライアントとのすり合わせが終わった段階で、バージョンを切り替えるなどタイミングを調整できる。
- モデルの差分調査がしやすい。
  - 同じモデルを更新すると、更新前後で差分がわかりにくい。
  - バージョンをわけておけば、v1とv2の２つのテーブル差分を調査することになりやりやすい。
- データソースの追加、撤退に柔軟に対応できる。
  - 新たなデータホルダーが増える、逆に今まで使えていたいデータが使えなくなるといったことがある。
  - v1はデータホルダーAのデータ、v2はデータホルダーBのデータとして開発、v2が使えなくなってもv1に切り戻すこともできる。

逆にデメリットとしては、以下のようなものがあります。

- データが2倍、3倍になる。
  - バージョンごとにモデルが増えるため、データ量が単純に増える。
  - 適切に過去バージョンの削除ルールを決めておく必要がある。
- バージョンごとのメタデータ管理が大変
  - 扱うデータが増えるということは、それだけデータ品質に関する管理コストもあがる。
  - バージョンごとのyamlをうまく活用する必要がある、


## まとめ
ナウキャストでは、データ自体がクライアントへの提供価値と直結するため、データasプロダクトとして、開発していく必要があります。

- データの差分調査を簡単にしたい。
- 過去バージョンの撤退ルールを整備したい。
- バージョン切り替えの運用ルールを決めたい。
  
などまだまだ課題は山積みなので、試行錯誤しつつデータ開発を楽しんでいきます！
