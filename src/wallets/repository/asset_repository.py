from db_config.database import engine
from sqlalchemy import select
from src.wallets.models import Wallet, Asset

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import contains_eager





class AssetRepository():

    async def return_asset_per_code(self, code):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Asset).filter(Asset.code==code)

            assets = await session.execute(query)
            result = assets.scalars().first()
            await session.commit()
        return result


    

asset_rep_link = AssetRepository()