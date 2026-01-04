# アーキテクチャ設計書 (Architecture Design Document)

## 1. 概要
本プロジェクト (`kapp-backend`) は、Pythonの **FastAPI** フレームワークを使用し、保守性とテスト容易性、拡張性を高めるために **クリーンアーキテクチャ (Clean Architecture)** の概念（オニオンアーキテクチャ）を採用しています。

ビジネスロジック（ドメイン）を中心に据え、フレームワークやデータベースなどの外部要素への依存を排除する設計となっています。

## 2. ディレクトリ構造

```text
app/
├── domain/                  # [Core] 外部依存を一切持たないビジネスロジックの中核
│   ├── model/               # エンティティ・値オブジェクト
│   └── repository/          # リポジトリのインターフェース (抽象定義)
│
├── usecase/                 # [Application] アプリケーション固有のビジネスフロー
│   ├── dto/                 # UseCaseの入出力データ構造 (DTO)
│   └── {feature}_usecase.py # 具体的なユースケース実装
│
├── adapter/                 # [Infrastructure] 詳細な技術的実装
│   ├── repository/          # DomainのリポジトリI/Fを実装する具象クラス (DB操作など)
│   └── gateway/             # 外部APIクライアントなど
│
├── presentation/            # [Interface] 外部との接点 (Web API, CLI)
│   ├── api/                 # FastAPI Router / Controller
│   └── schema/              # APIのリクエスト/レスポンス定義 (Pydantic)
│
├── main.py                  # アプリケーションエントリーポイント (DI設定)
└── config.py                # 環境変数・設定管理
```

## 3. レイヤーの詳細と役割

依存の方向は常に **外側（詳細） → 内側（抽象）** に向かいます。内側のレイヤーは外側のレイヤーについて一切関知しません。

### 3.1. Domain Layer (ドメイン層)
*   **役割**: ビジネスの中核となるルール、データの形、操作の定義。
*   **構成要素**:
    *   **Model (Entity/Value Object)**: ビジネスデータを表現するオブジェクト。Pydanticを使用。
    *   **Repository Interface**: データの永続化を行うための抽象インターフェース。Pythonの **Protocol** を使用して定義することを推奨（継承不要なダックタイピング）。
*   **依存関係**: **なし**。他のどのレイヤーにも依存しない。

### 3.2. UseCase Layer (ユースケース/アプリケーション層)
*   **役割**: ドメインオブジェクトを操作し、ユーザーの要求（「ユーザー登録する」「一覧を取得する」など）を実現する。
*   **構成要素**:
    *   **Service / Interactor**: 具体的な処理フロー。
    *   **DTO (Data Transfer Object)**: UseCaseへの入力や出力データの型定義。ドメインモデルとの変換ロジック（`to_domain`, `from_domain`）はここに持たせる。
*   **依存関係**: **Domain Layer** にのみ依存する。具体的なDBの実装やWebフレームワークのことは知らない。

### 3.3. Adapter Layer (アダプター/インフラ層)
*   **役割**: Domain層やUseCase層で定義されたインターフェースを、具体的な技術（PostgreSQL, Redis, AWS S3など）を使って実装する。
*   **構成要素**:
    *   **Repository Implementation**: SQLModel (SQLAlchemy) を使用して実装。
    *   **ORM Model**: DBテーブル定義。循環参照を避けるため、`app/adapter/orm/model.py` などの1ファイルに集約することを許容する。
*   **依存関係**: **Domain Layer** (インターフェース定義) に依存する。

### 3.4. Presentation Layer (プレゼンテーション層)
*   **役割**: 外部（クライアント）からの入力を受け取り、適切なUseCaseを呼び出し、結果をレスポンスとして返す。
*   **構成要素**:
    *   **Router (Controller)**: エンドポイントの定義。
    *   **Schema**: APIの入出力定義 (Request Body / Response Body)。
*   **依存関係**: **UseCase Layer** に依存する。

## 4. 命名規則 (Naming Conventions)

| 種別 | 規則 | 例 |
| :--- | :--- | :--- |
| **ファイル名** | スネークケース | `user_repository.py`, `create_user.py` |
| **クラス名** | パスカルケース | `UserRepository`, `CreateUserUseCase` |
| **変数/関数名** | スネークケース | `get_user_by_id`, `user_data` |
| **定数** | アッパースネーク | `MAX_LOGIN_ATTEMPTS`, `DEFAULT_TIMEOUT` |

## 5. 開発フロー
機能追加時は、以下の順序（内側から外側）で実装することを推奨します。

1.  **Domain**: モデルとリポジトリI/Fを定義。
2.  **UseCase**: ビジネスロジックを実装。
3.  **Adapter**: データの保存先（DB等）を実装。
4.  **Presentation**: APIエンドポイントを定義し、全体を繋ぎ込む。
5.  **DI (Dependency Injection)**: `main.py` 等で具象クラスを注入する。
