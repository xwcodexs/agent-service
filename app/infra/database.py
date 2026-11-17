from langchain_community.document_loaders.notiondb import DATABASE_URL

from collections.abc import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
if not settings.db or not settings.db.url:
    raise RuntimeError("db.url is required")
DATABASE_URL = settings.db.url

#数据库引擎
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo = settings.db.echo,
    pool_size = settings.db.pool_size,
    max_overflow = settings.db.max_overflow,
    pool_recycle = settings.db.pool_recycle,
    pool_pre_ping = True,
    # 连接超时（秒）。不设置时 asyncpg 会干等到 60 秒才报错，期间一行日志都没有，
    # 表现为"启动后卡住、什么都不显示"。
    connect_args = {"timeout": settings.db.connect_timeout},
)
#Session工厂
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,  # 执行查询前不自动 flush
    expire_on_commit=False,  # commit 后保留 ORM 对象中的属性值
)
#获取seesion工具
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """为每个FastAPI请求创建独立的AsyncSession,适用于依赖注入"""
    async with AsyncSessionFactory() as session:
        yield session
#释放数据库连接池
async def close_database() -> None:
    """关闭数据库引擎并释放连接池中的连接。应在应用关闭时调用"""
    await engine.dispose()
    logger.info("Database engine disposed")
# 6. 数据库健康检查
async def check_database() -> None:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    logger.info("数据库连接池初始化成功~✅️")