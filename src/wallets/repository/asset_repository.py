from db_config.database import engine
from sqlalchemy import select
from src.wallets.models import Asset, Blockchain
from src.wallets.schemas import NewAssetSchema

from sqlalchemy.ext.asyncio import async_sessionmaker


class AssetRepository:
    """
    Asynchronous asset repository providing methods
    for interacting with asset objects in the database.
    """

    async def return_asset_per_code(self, code: str) -> Asset:
        """
         Retrieves an asset object from the
         database based on its unique code.

        Args:
            code(str): The unique identifier (code) of the asset to retrieve.

        Returns:
            result(Aset) : The retrieved asset object if found, otherwise None.
        """
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Asset).filter(Asset.code == code)

            assets = await session.execute(query)
            result = assets.scalars().first()
            await session.commit()
        return result


    async def create_asset(self, asset_data: NewAssetSchema, blockchain: Blockchain):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            asset = Asset(type = asset_data.type,
                    text = asset_data.text,
                    decimal_places = asset_data.decimal_places,
                    title = asset_data.title,
                    code = asset_data.code,
                    blockchain_id = blockchain.id)
            session.add(asset)
            await session.commit()
        return asset






asset_rep_link = AssetRepository()
