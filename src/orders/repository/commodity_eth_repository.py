from sqlalchemy.ext.asyncio import async_sessionmaker
from db_config.database import engine


from src.orders.services.commodity_abstract_services import CommodityAbstractService
from src.orders.models import Commodity
from src.wallets.models import Wallet, Asset
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload



class CommodityEthRepository(CommodityAbstractService):

    async def save_commodity_in_db(self, commodity_data):
        print('===commodity_data===')
        print(commodity_data)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            commodity = Commodity(
                wallet_id=int(commodity_data['wallet']),
                title=commodity_data['title'],
                price=float(commodity_data['price']),
                photo=commodity_data['photo']
            )
            session.add(commodity)
            await session.commit()
            commodity = await session.execute(select(Commodity)\
                                        .options(selectinload(Commodity.wallet).selectinload(Wallet.asset))\
                                        .filter_by(id=commodity.id)
                                    )
            commodity = commodity.scalars().one()

        return commodity


    async def return_commodities_for_list(self):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:

            query = select(Commodity).options(joinedload(Commodity.wallet).joinedload(Wallet.asset))
            result = await session.execute(query)
            commodities = result.scalars().all()
            print(f"Query returned {len(commodities)} results")
            await session.commit()

        return commodities

commodity_eth_rep_link = CommodityEthRepository()