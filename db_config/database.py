import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# filefield import
from sqlalchemy_file.storage import StorageManager
from libcloud.storage.drivers.local import LocalStorageDriver

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

# from .models import Base

# from src.users.models import User, Message
# from src.wallets.models import Wallet, Asset, Blockchain
# from src.etherium.models import Transaction
# from src.orders.models import Commodity, Order


# !!! вынести ссылку в .env
SQLALCHEMY_DATABASE_URL = "postgresql://maxim:12345qwert@localhost:5432/cryptowallet_db"

# filefield storage logic
os.makedirs("./media/attachment", 0o777, exist_ok=True)
container = LocalStorageDriver("./media").get_container("attachment")
StorageManager.add_storage("default", container)


       

ASYNCSQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://maxim:12345qwert@localhost:5432/cryptowallet_db"
engine = create_async_engine(ASYNCSQLALCHEMY_DATABASE_URL)
Base = declarative_base()
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)




async def get_async_session():
    async with async_session() as session:
        yield session