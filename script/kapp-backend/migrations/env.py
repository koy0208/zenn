# 一言で言うと、「Alembic にあなたのアプリの『DB接続先』と『テーブル定義(SQLModel)』を教える場所」 です。

#   具体的に何をしているのか、3つのポイントで説明します。

#   1. データベースへの接続設定
#   AlembicがDBに接続して現在のテーブル状態を確認するために必要です。

#    1 # env.pyの中で...
#    2 config = context.config
#    3 url = settings.DATABASE_URL  # あなたのアプリの設定からDB接続URLを取得
#    4 context.configure(url=url, ...) # Alembicに教える

#   2. モデル定義（メタデータ）の登録
#   「Pythonコードで書いたテーブル定義」をAlembicに伝えます。これと「実際のDB」を比較して、差分（マイグレーションファイル）を作ります。
#    1 from sqlmodel import SQLModel
#    2 from app.adapter.orm.user_orm import UserORM # モデルをインポートすることで登録される
#    3
#    4 target_metadata = SQLModel.metadata # これをAlembicに渡す
#   ここが None だと、--autogenerate をしても「変更なし」と言われてしまいます。

#   3. オフラインモードとオンラインモードの分岐
#    * オフラインモード: DBに接続せず、ただSQLファイルだけを出力したい場合に使われます。
#    * オンラインモード: 実際にDBに接続して、マイグレーションを実行する場合（upgrade head など）に使われます。通常はこちらが動きます。

#   ---

#   まとめ:
#   env.py は、あなたのアプリケーションコード（app/）と、マイグレーションツール（Alembic）をつなぐ 「接着剤」 のような役割を果たしています。

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# --- ここから追加 ---
import os
import sys

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.getcwd())

from app.config import settings
from sqlmodel import SQLModel

# モデルをインポートしないとメタデータに登録されないため、ここでインポート
from app.adapter.orm.user_orm import UserORM

# ------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# target_metadata = None
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this version we keep the synchronous connection for simplicity,
    but Alembic's default template for async would look different.
    Since we are using synchronous SQLAlchemy for now, we'll use the sync runner.
    """
    from sqlalchemy import create_engine

    connectable = create_engine(settings.DATABASE_URL)

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # 今回は同期型SQLAlchemyを使用しているため、シンプルな同期実行にします
    from sqlalchemy import create_engine

    connectable = create_engine(settings.DATABASE_URL)

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
