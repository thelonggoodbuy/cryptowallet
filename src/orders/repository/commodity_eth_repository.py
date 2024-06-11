from sqlalchemy.ext.asyncio import async_sessionmaker
from db_config.database import engine


from src.orders.repository.commodity_abstract_repository import CommodityAbstractRepository
from src.orders.models import Commodity, Order
from src.wallets.models import Wallet, Asset
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload




class CommodityEthRepository(CommodityAbstractRepository):

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
            query = select(Commodity).outerjoin(Order, Commodity.id == Order.commodity_id)\
                                    .options(joinedload(Commodity.wallet)\
                                    .joinedload(Wallet.asset))\
                                    .filter(Order.id == None)
            
            result = await session.execute(query)
            commodities = result.scalars().all()
            print(f"Query returned {len(commodities)} results")
            await session.commit()
        return commodities



    async def return_commodity_by_id(self, commodity_id):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Commodity).options(joinedload(Commodity.wallet)).filter(Commodity.id == int(commodity_id)).limit(1)
            result = await session.execute(query)
            commodity = result.scalars().one()
            await session.commit()
        return commodity
    

commodity_eth_rep_link = CommodityEthRepository()