# FAQ & 開発ナレッジ (FAQ & Knowledge)

プロジェクト開発中に生じた疑問とその回答、技術的な意思決定の背景をまとめる。

## 1. アーキテクチャ・設計方針

### Q. なぜ `User` (Domain) と `UserORM` (Adapter) を分けるのか？
**A. ドメインロジックをDBの実装詳細から守るため（クリーンアーキテクチャ）。**
*   **`User`**: 純粋なビジネスデータ。DBが何かを知らない。
*   **`UserORM`**: DBへの保存用クラス。テーブル名やカラム型などDBの都合を持つ。
*   もし分けないと、DBライブラリを変更する際にビジネスロジックまで修正が必要になり、保守性が下がる。

### Q. `to_domain`, `from_domain` メソッドはなぜ必要？
**A. 異なる2つの世界（DomainとAdapter）をつなぐ翻訳機として必須。**
*   **場所**: `UserORM` クラス（Adapter層）に実装する。
*   **理由**: Domain層はAdapter層（ORM）を知ってはいけないため、Adapter側が「Domainを知っている」状態にして変換を担当する。
*   ドメインモデルに `to_table` メソッドを作ると、依存の逆流（Domain → Adapter）になるためNG。

### Q. `Relationship` と `back_populates` の役割は？
**A. テーブル間の繋がりをオブジェクトとして操作するための設定。**
*   **カラムではない**: `author_id` はDBの数値カラムだが、`author` (`Relationship`) はPython上のオブジェクトへのリンク。
*   **双方向**: `back_populates` を双方のモデルに書くことで、`article.author`（親を取得）と `user.articles`（子のリストを取得）の両方が可能になる。
*   **同期**: メモリ上で片方を変更すると、もう片方も自動的に更新されるため不整合が起きにくい。
*   **片方向**: 必ずしも双方向にする必要はない。不要な場合は片側のみに定義することも可能。

### Q. DTOの変換方向（DTO ↔ Domain）はどうあるべき？
**A. UseCase層を中心に入出力の責務を明確にする。**
1.  **入力時 (DTO → Domain)**:
    *   外部からのデータ（APIリクエスト等）を、アプリ内部で扱える形式（Domain Model）に変換する。
2.  **出力時 (Domain → DTO)**:
    *   アプリ内部の結果（Domain Model）を、外部に見せる形式（APIレスポンス等）に変換する。パスワード除去やフォーマット調整もここで行う。
*   **NG**: Domain Model が DTO を知ること（`Article.from_dto(...)`）は、依存の方向が逆転するため禁止。

### Q. `to_domain`, `from_domain` はどこに実装すべき？
**A. DTO側に実装するのが推奨（Factory Method パターン）。**
*   **メリット**:
    *   UseCaseが「マッピング作業」から解放され、ビジネスロジック（流れ）の記述に集中できる。
    *   複数のUseCaseで同じDTOを使う場合、変換ロジックを再利用できる。
*   **例**:
    *   `ArticleCreateInput.to_domain()`: 自身のデータを使って `Article` インスタンスを生成して返す。
    *   `ArticleOutput.from_domain(article)`: `Article` を受け取って自身のインスタンスを生成するクラスメソッド。

### Q. `from_domain` は `@staticmethod` か `@classmethod` か？
**A. `@classmethod` が推奨。**
*   継承時にサブクラスのインスタンスを正しく生成できるため（`cls(...)` を使用）。
*   `@staticmethod` でも動作はするが、クラス名をハードコードする必要があり柔軟性に欠ける。

## 2. 実装技術・ライブラリ

### Q. `Optional[T]` は使わないの？
**A. Python 3.10以降では `T | None` が推奨。**
*   `typing.Optional` は古い書き方。
*   同様に `List[T]` ではなく `list[T]`、`Dict` ではなく `dict` を使用する。

### Q. `Depends(get_db)` はなぜ必要？
**A. DBセッションのライフサイクル管理をFastAPIに任せるため。**
*   **安全性**: 1リクエストにつき1セッションを作成し、処理終了後に必ず閉じる（`finally: db.close()`）ことを保証できる。
*   **テスト容易性**: `app.dependency_overrides` を使うことで、テスト時に簡単にDBをモック（偽物）に差し替えられる。

### Q. SQLAlchemyではなくSQLModelを使う判断について
**A. Adapter層（ORM）のみ `SQLModel` を採用し、共通カラムを効率化。**
*   **Domain層**: 依然として純粋なPydanticモデルを使用（`SQLModel`には依存させない）。
*   **Adapter層**: `SQLAlchemy` の `Base` の代わりに `SQLModel` を使用。
    *   **メリット**: `BaseORM` クラスを作成し、全テーブル共通の `created_at`, `updated_at` などを簡単に定義・継承できる。
    *   **注意**: クリーンアーキテクチャを守るため、Domain層で `SQLModel` を使ってはいけない。

## 3. データベース・マイグレーション

### Q. `migrations/env.py` とは何？
**A. AlembicがDB接続情報とモデル定義を知るための設定ファイル。**
*   **役割**: アプリのDB URL (`settings.DATABASE_URL`) と、テーブル定義 (`SQLModel.metadata`) をAlembicに伝える。
*   これがないと、マイグレーションの自動生成 (`--autogenerate`) が機能しない。
*   initファイルは自動で生成される。


### Q. `created_at` / `updated_at` はPythonで入れる？
**A. いいえ、データベース（PostgreSQL）側で自動生成される。**
*   `server_default=func.now()`: INSERT時に現在時刻が入る。
*   `onupdate=func.now()`: UPDATE時に自動更新される。
*   **重要**: Python側で保存直後の値を知るには、`db.refresh(obj)` を実行してDBから値を読み直す必要がある。

## 4. 外部ストレージ (S3)

### Q. なぜ S3 を直接使わず `FileStorage` インターフェースを作るのか？
**A. 特定のクラウドベンダー (AWS) へのロックインを防ぎ、テストを容易にするため。**
*   **柔軟性**: 将来的に Google Cloud Storage や Azure Blob Storage、あるいはローカルディスクに切り替える際、UseCase 層のコードを一切変更せずに済む。
*   **テスト**: ローカルでの開発や自動テスト時に、S3に接続せず「メモリ内に保存するだけのFakeStorage」に差し替えることが容易になる。

### Q. S3の認証情報はどこで管理する？
**A. AWS SDK (boto3) のデフォルト認証チェーンに任せる。**
*   コード内や `config.py` で Access Key を明示的に扱わないように変更済み。
*   **SSOの場合**: ローカルで `aws sso login` した状態で、環境変数 `AWS_PROFILE=your-profile-name` を指定してアプリを起動すれば自動的に認証される。
*   **本番環境**: IAMロールなどが自動的に使用される。
*   **Access Keyを使う場合**: 環境変数 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` をセットすれば、boto3が勝手に読み込む。
