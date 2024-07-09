import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# filefield import
from sqlalchemy_file.storage import StorageManager
from libcloud.storage.drivers.local import LocalStorageDriver

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

import os


# !!! вынести ссылку в .env
# SQLALCHEMY_DATABASE_URL = "postgresql://maxim:12345qwert@localhost:5432/cryptowallet_db"

os.makedirs("./media/attachment", 0o777, exist_ok=True)

container = LocalStorageDriver("./media").get_container("attachment")
StorageManager.add_storage("default", container)


POSTGRES_DB=os.environ.get('POSTGRES_DB')
POSTGRES_USER=os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD=os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST=os.environ.get('POSTGRES_HOST')
POSTGRES_PORT=os.environ.get('POSTGRES_PORT')

ASYNCSQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# print('====================================')
# print('os environ in db')
# print('====================================')
# print(os.environ)

engine = create_async_engine(ASYNCSQLALCHEMY_DATABASE_URL)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session():
    async with async_session() as session:
        yield session
