from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings
from typing import AsyncGenerator
from sqlalchemy import text

# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # 在控制台输出SQL语句，生产环境可以设为False
    pool_pre_ping=True,  # 检查连接是否仍然有效
    pool_recycle=3600,  # 每小时回收连接
)

# 创建异步session工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 基础模型类
Base = declarative_base()

# 依赖注入：获取数据库会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖函数
    使用示例：
        async def some_endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """
    初始化数据库，创建所有表
    在应用启动时调用
    """
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT DATABASE()"))
        db_name = result.scalar()
        print("当前连接数据库：", db_name)
        
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表已成功创建")

async def close_db() -> None:
    """
    关闭数据库连接
    在应用关闭时调用
    """
    await engine.dispose()
    print("关闭数据库连接")