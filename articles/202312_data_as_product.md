---
title: "データasプロダクト"
emoji: "📚"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: [データマネジメント]
published: false
---

## はじめに
近ごろ、**データマネジメント**の領域が盛り上がってきているように思います。ビジネス活動の副産物としての立ち位置だったデータを、データそのものをビジネス資産として捉え、マネジメントしていこうというわけです。データマネジメントのバイブルである「DMBOOK」は、データをこう定義しています。
>データは万物に関する事実を表現する役割を持つ

つまりデータとは、


こう書かれています。

https://www.amazon.co.jp/%E3%83%87%E3%83%BC%E3%82%BF%E3%83%9E%E3%83%8D%E3%82%B8%E3%83%A1%E3%83%B3%E3%83%88%E7%9F%A5%E8%AD%98%E4%BD%93%E7%B3%BB%E3%82%AC%E3%82%A4%E3%83%89-%E7%AC%AC%E4%BA%8C%E7%89%88-DAMA-International/dp/4296100491





データメッシュの概要、データ


## データメッシュとは？
## データasプロダクトとは？

>For a distributed data platform to be successful, domain data teams must apply product thinking with similar rigor to the datasets that they provide; considering their data assets as their products and the rest of the organization's data scientists, ML and data engineers as their customers.
訳：
分散データプラットフォームが成功するためには、ドメインデータチームが提供するデータセットにも同様の厳密さでプロダクト思考を適用しなければならない。データ資産をプロダクトとみなし、それ以外の組織のデータサイエンティスト、ML、データエンジニアを顧客とみなすのだ。
[引用](https://martinfowler.com/articles/data-monolith-to-mesh.html#DataAndProductThinkingConvergence)


## プロダクトとしてのデータに求められるもの

- Discoverable	発見しやすい
- Addressable	所在や形式が明確でアクセスしやすい
- Trustworthy	データ品質が担保されて信頼性がある
- Self-Describing	分析に利用しやすいように収集・整備されていて理解しやすい説明も記述されている
- Inter operable 他ドメインのデータと組合せて使えるように標準に準拠している
- Secure	プライバシーや規制に違反するリスクを管理できている

### Discoverable
検索しやすい
データカタログ
データの説明
### Addressable
同じフォーマット、アクセスしやすい

### Trustworthy
信頼性
SLO
The target value or range of a data integrity (quality) indicator vary between domain data products
### Self-describing
理解に最小限の労力で、各ドメインが自己消費できる。
### Inter-operable
ドメインをまたいでデータを結合してしようできる。
データメッシュで、分散化していなければ関係なさそうだが、異なるテーブルで、同じ列名が同音異義語で複数あるなどは混乱する。
### Secure
アクセスポリシー

## 参考
https://towardsdatascience.com/data-as-a-product-vs-data-products-what-are-the-differences-b43ddbb0f123
https://martinfowler.com/articles/data-monolith-to-mesh.html#DataAndProductThinkingConvergence
https://qiita.com/moritata9/items/6844afb1e2ea54d8e984