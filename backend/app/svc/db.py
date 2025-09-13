import os, sqlalchemy as sa
from databases import Database

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ai.db")
db = Database(DATABASE_URL)
metadata = sa.MetaData()

ai_settings = sa.Table(
    "ai_settings", metadata,
    sa.Column("user_id", sa.String, primary_key=True),
    sa.Column("key", sa.String, primary_key=True),
    sa.Column("data", sa.JSON, nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))
)

risk_limits = sa.Table(
    "risk_limits", metadata,
    sa.Column("user_id", sa.String, primary_key=True),
    sa.Column("max_symbol", sa.Float, nullable=False, server_default="0"),
    sa.Column("max_total", sa.Float, nullable=False, server_default="0"),
    sa.Column("daily_loss", sa.Float, nullable=False, server_default="0"),
    sa.Column("window", sa.String, nullable=False, server_default="00:00-23:59"),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))
)

strategy_runs = sa.Table(
    "strategy_runs", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("user_id", sa.String, nullable=False),
    sa.Column("kind", sa.String, nullable=False),
    sa.Column("payload", sa.JSON),
    sa.Column("ok", sa.Boolean, server_default=sa.text("FALSE")),
    sa.Column("reason", sa.String),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"))
)

sentiment = sa.Table(
    "sentiment", metadata,
    sa.Column("symbol", sa.String, primary_key=True),
    sa.Column("ts", sa.DateTime(timezone=True), primary_key=True, server_default=sa.text("CURRENT_TIMESTAMP")),
    sa.Column("score", sa.Float, nullable=False)
)

engine = sa.create_engine(DATABASE_URL.replace("+aiosqlite",""), future=True)

def init_schema():
    metadata.create_all(engine)

async def init_pool():
    if not db.is_connected:
        await db.connect()

async def close_pool():
    if db.is_connected:
        await db.disconnect()
