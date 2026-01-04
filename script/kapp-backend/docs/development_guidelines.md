# 開発ガイドライン & アーキテクチャ設計 (Development Guidelines & Architecture Design)

本プロジェクトの開発において遵守すべきルール、アーキテクチャ方針、およびコマンドをまとめる。

## 1. プロジェクト概要 (Project Overview)
本プロジェクト (`kapp-backend`) は、Pythonの **FastAPI** フレームワークを使用したバックエンドアプリケーションであり、**クリーンアーキテクチャ (オニオンアーキテクチャ)** を採用している。

### 1.1 技術スタック (Tech Stack)
*   **言語**: Python 3.10+
*   **Webフレームワーク**: FastAPI
*   **パッケージ管理**: `uv`
*   **ORM**: SQLAlchemy / SQLModel
*   **DBマイグレーション**: Alembic
*   **テスト**: pytest

### 1.2 アーキテクチャ方針
ビジネスロジック（ドメイン）を中心に据え、外部要素（DB、フレームワーク）への依存を排除する。
依存の方向は常に **外側 (Infrastructure/Presentation) → 内側 (UseCase → Domain)** とする。

## 2. ディレクトリ構成 (Directory Structure)
```text
app/
├── domain/                  # [Core] 外部依存を持たないビジネスロジックの中核
│   ├── model/               # エンティティ・値オブジェクト
│   └── repository/          # リポジトリのインターフェース (Protocol)
│
├── usecase/                 # [Application] アプリケーション固有のビジネスフロー
│   ├── dto/                 # UseCaseの入出力データ構造
│   └── {feature}_usecase.py # ユースケース実装
│
├── adapter/                 # [Infrastructure] 詳細な技術的実装
│   ├── repository/          # DomainのリポジトリI/Fの具象実装 (SQLAlchemy等)
│   ├── orm/                 # DBテーブル定義 (ArticleORM等)
│   └── storage/             # 外部ストレージ (S3等) 実装
│
├── presentation/            # [Interface] 外部との接点 (Web API)
│   ├── api/                 # FastAPI Router
│   └── schema/              # APIリクエスト/レスポンス定義 (Pydantic)
│
├── main.py                  # エントリーポイント (DI設定)
└── config.py                # 設定管理
```

## 3. レイヤーの役割 (Layer Roles)

### 3.1 Domain Layer
*   **役割**: ビジネスの中核ルールとデータの定義。
*   **依存**: なし。
*   **リポジトリ**: `Protocol` を使用してインターフェースを定義する。

### 3.2 UseCase Layer
*   **役割**: ドメインオブジェクトを操作し、ビジネスフロー（「記事を更新する」など）を実現する。
*   **DTO**: 入出力データ型を定義。ドメインモデルとの変換ロジックを持つ。
*   **依存**: Domain Layer にのみ依存。

### 3.3 Adapter Layer
*   **役割**: 技術的な詳細（PostgreSQL, S3など）の実装。
*   **ORM**: `app/adapter/orm/model.py` にDBモデルを集約する。
*   **依存**: Domain Layer (インターフェース) に依存。

### 3.4 Presentation Layer
*   **役割**: HTTPリクエストを受け、UseCaseを呼び出し、レスポンスを返す。
*   **依存**: UseCase Layer に依存。

## 4. 実装ルール (Implementation Rules)

### 4.1 データベース接続とDI
*   **厳守**: DBセッション (`Session`) の管理は `Presentation` 層 (Router) で行う。
*   FastAPIの `Depends(get_db)` を使用して取得し、`Repository` -> `UseCase` の順に注入する。
*   UseCase内で `Session` を直接生成したり、グローバルな `db` を参照してはならない。

### 4.2 SQLAlchemyの実装注意 (SQLAlchemy Implementation)
*   **更新処理 (`db.merge`)**:
    *   `db.merge(obj)` は、引数のオブジェクトをセッションに接続せず、**新しい永続化インスタンス**を返す。
    *   そのため、**必ず戻り値を受け取る**こと。
    *   **Bad**: `db.merge(obj)` (この後 `db.refresh(obj)` するとエラーになる)
    *   **Good**: `obj = db.merge(obj)` (永続化されたインスタンスを受け取る)

### 4.3 型注釈 (Type Hinting)
*   **Python 3.10+ スタイル** を使用。
    *   `Optional[T]` ではなく **`T | None`** を使用。
    *   `List[T]` ではなく **`list[T]`** を使用。
*   全ての関数・メソッドに型注釈を付与する。

### 4.4 データベースマイグレーション
*   **Alembic** を使用して管理する。`Base.metadata.create_all()` は禁止。

### 4.5 エラーハンドリング
*   **UseCase層**: ビジネスエラーは `ValueError` 等の標準例外または専用例外を投げる。
*   **Presentation層**: UseCaseからの例外をキャッチし、適切な `HTTPException` (404等) に変換する。

## 5. 命名規則 (Naming Conventions)
*   **ファイル名**: スネークケース (`user_repository.py`)
*   **クラス名**: パスカルケース (`UpdateArticleUseCase`)
*   **変数/関数名**: スネークケース (`get_article_by_id`)

## 6. 開発フロー
1. **Domain**: モデルとリポジトリI/Fの定義。
2. **UseCase**: ビジネスロジックの実装。
3. **Adapter**: DB操作等の具象実装。
4. **Presentation**: APIエンドポイントの実装。

## 7. コマンドリファレンス (Command Reference)

### 開発・テスト
```bash
# サーバー起動
uv run uvicorn app.main:app --reload

# テスト実行
uv run pytest
```

### マイグレーション
```bash
# 生成
uv run alembic revision --autogenerate -m "message"
# 適用
uv run alembic upgrade head
```
