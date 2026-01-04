# Project Context: Kapp Backend

このファイルは、AIアシスタント（Gemini）がプロジェクトの文脈、ルール、技術スタックを理解するためのコンテキスト情報です。

## 1. 開発ガイドライン & アーキテクチャ
詳細な設計方針、ディレクトリ構造、実装ルール、命名規則については以下のドキュメントを最優先で参照してください。

*   **[docs/development_guidelines.md](docs/development_guidelines.md)**

## 2. 技術スタックの要約
*   **Framework**: FastAPI (Python 3.10+)
*   **Package Manager**: `uv`
*   **ORM**: SQLAlchemy / SQLModel
*   **Migration**: Alembic
*   **Architecture**: Clean Architecture (Onion Architecture)

## 3. 重要な実装上の注意
*   **SQLAlchemy**: `db.merge(obj)` を使用する際は、必ず `obj = db.merge(obj)` のように戻り値を受け取ること。
*   **DI**: DBセッションはPresentation層で取得し、Repository/UseCaseへ注入する。

## 4. クイックコマンド
*   テスト: `uv run pytest`
*   起動: `uv run uvicorn app.main:app --reload`
*   マイグレーション適用: `uv run alembic upgrade head`