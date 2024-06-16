from db_config.database import engine
from sqlalchemy import select
from src.wallets.models import Asset

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


asset_rep_link = AssetRepository()
