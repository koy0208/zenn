# 開発ガイドライン (Development Guidelines)

本プロジェクトの開発において遵守すべきルールと方針をまとめる。AIアシスタントおよび開発者は本ドキュメントを参照すること。

## 1. アーキテクチャ (Architecture)
**クリーンアーキテクチャ (オニオンアーキテクチャ)** を採用。
依存の方向は **外側 (Infrastructure/Presentation) → 内側 (UseCase → Domain)** とする。

### ディレクトリ構成
- `app/domain`: 外部依存を持たないビジネスロジック・モデル。
- `app/usecase`: アプリケーション固有のビジネスフロー。Domainのみに依存。
- `app/adapter`: DBや外部APIの実装詳細。DomainのI/Fを実装する。
- `app/presentation`: Web API (FastAPI)。UseCaseを利用する。

## 2. 実装ルール (Implementation Rules)

### 2.1 データベース接続とDI (Database & Dependency Injection)
*   **厳守**: DBセッションの管理は `app/presentation` (Router) 層で行う。
*   FastAPIの `Depends` を使用して `Session` を取得し、それを Repository → UseCase の順に注入する。
*   UseCase内で `Session` を直接生成したり、グローバルな `db` オブジェクトを参照してはならない。

```python
# GOOD
@router.post("/")
def create_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Response:
    repo = UserRepositoryImpl(db)
    usecase = CreateUserUseCase(repo)
    return usecase.execute(...)
```

### 2.2 型注釈 (Type Hinting)
*   **Python 3.10+ スタイル** を使用すること。
    *   `Optional[T]` ではなく **`T | None`** を使用する。
    *   `List[T]`, `Dict[K, V]` ではなく **`list[T]`, `dict[K, V]`** を使用する。
*   **全ての関数・メソッド** に引数と戻り値の型注釈を付与すること。

### 2.3 データベースマイグレーション (Migration)
*   **Alembic** を使用してスキーマ変更を管理する。
*   コード内での `Base.metadata.create_all()` の使用は**禁止**。
*   モデル (`app/adapter/orm/*.py`) を変更した際は、必ずマイグレーションファイルを生成・適用する。

### 2.4 エラーハンドリング (Error Handling)
*   **UseCase層**: ビジネスロジックのエラー（例: IDが見つからない）は、Python標準の例外（`ValueError` 等）または専用の例外クラスを発生させる。
*   **Presentation層 (Router)**: UseCaseからの例外をキャッチし、適切な `HTTPException` に変換する。
    *   `ValueError` (IDなし) -> `404 Not Found`
    *   想定外のエラー -> そのまま伝播させ `500 Internal Server Error` とする。

## 3. コマンドリファレンス (Command Reference)

### 開発サーバー起動
```bash
make dev
# または
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### マイグレーション (Alembic)
**変更の検出とファイル生成:**
```bash
uv run alembic revision --autogenerate -m "Describe change here"
```

**変更の適用 (DBへの反映):**
```bash
uv run alembic upgrade head
```
