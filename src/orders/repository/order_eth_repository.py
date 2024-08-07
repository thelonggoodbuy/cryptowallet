from sqlalchemy.ext.asyncio import async_sessionmaker
from db_config.database import engine

from src.orders.models import Order
from src.etherium.models import Transaction
from src.orders.repository.order_abstract_repository import OrderAbstractRepository
from src.orders.models import Commodity
from src.wallets.models import Wallet
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from src.orders.schemas import UpdateOrderSchema
from sqlalchemy import asc
from src.wallets.services.wallet_etherium_service import WalletEtheriumService


class OrderEthRepository(OrderAbstractRepository):
    @classmethod
    async def create_new_order_for_pending_transaction(cls, transaction, commodity):
        # async def save_commodity_in_db(self, commodity_data):
        #     print('===commodity_data===')
        #     print(commodity_data)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            order = Order(
                commodity=commodity,
                transaction=transaction,
                order_status="transaction_pending",
            )
            session.add(order)
            await session.commit()
        #         commodity = await session.execute(select(Commodity)\
        #                                     .options(selectinload(Commodity.wallet).selectinload(Wallet.asset))\
        #                                     .filter_by(id=commodity.id)
        #                                 )
        #         commodity = commodity.scalars().one()

        return order

    # async def return_commodities_for_list(self):
    #     async_session = async_sessionmaker(engine, expire_on_commit=False)
    #     async with async_session() as session:

    #         # query = select(Commodity).options(joinedload(Commodity.wallet).joinedload(Wallet.asset))
    #         query = select(Commodity).outerjoin(Order, Commodity.id == Order.commodity_id)\
    #                                 .options(joinedload(Commodity.wallet)\
    #                                 .joinedload(Wallet.asset))\
    #                                 .filter(Order.id == None)

    #         result = await session.execute(query)
    #         commodities = result.scalars().all()
    #         print(f"Query returned {len(commodities)} results")
    #         await session.commit()

    #     return commodities
    async def return_orders_tied_with_pending_transactions(self):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = (
                select(Order)
                .options(joinedload(Order.transaction))
                .filter(Order.order_status == "transaction_pending")
            )
            result = await session.execute(query)
            orders = result.scalars().all()

        return orders

    async def update_status_order(self, update_order_datail: UpdateOrderSchema):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = (
                select(Order)
                .options(joinedload(Order.commodity), joinedload(Order.transaction))
                .filter(Order.id == update_order_datail.order_id)
            )
            result = await session.execute(query)
            order = result.scalars().first()

            print("***")
            print(update_order_datail)
            print("***")

            order.order_status = update_order_datail.status
            if update_order_datail.return_transaction_id:
                order.return_transaction_id = update_order_datail.return_transaction_id
            session.add(order)
            await session.commit()
            print("========info from repository=====")
            print(order.order_status)
            print("=================================")
        return order

    async def return_order_tied_with_pending_objects(self, order_id):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = (
                select(Order)
                .options(joinedload(Order.transaction), joinedload(Order.commodity))
                .filter(Order.id == order_id)
            )
            result = await session.execute(query)
            order = result.scalars().first()

        return order

    async def get_oldest_delivery(self):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = (
                select(Order)
                .options(joinedload(Order.transaction), joinedload(Order.commodity))
                .filter(Order.order_status == "delivery")
                .order_by(asc(Order.date_time_transaction))
            )

            result = await session.execute(query)
            order = result.scalars().first()
        return order

    async def get_all_users_orders_by_user_id(self, user_id):
        users_wallets_addresses = list(
            await WalletEtheriumService.return_all_wallets_adresses_per_user_id(user_id)
        )

        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = (
                select(Order)
                .join(Order.commodity)  # Join Order with Commodity
                .join(
                    Commodity.wallet
                )  # Join Commodity with Wallet фактически он дает списко оформленных заказов на кошельки привязанные к товару
                .join(Wallet.user)  # Join Wallet with User
                .options(
                    joinedload(Order.transaction),
                    joinedload(Order.return_transaction),
                    joinedload(Order.commodity)
                    .joinedload(Commodity.wallet)
                    .joinedload(Wallet.user),
                )
                .filter(
                    Order.transaction.has(
                        Transaction.send_from.in_(users_wallets_addresses)
                    )
                )
            )  # Filter by User.id

            result = await session.execute(query)
            users_orders = result.scalars().all()

        return users_orders

    # async def geturn_all_users_orders_by_user_id(self, user_id):
    #     async_session = async_sessionmaker(engine, expire_on_commit=False)
    #     async with async_session() as session:

    #         query = select(Order).options(joinedload(Order.transaction),
    #                                 joinedload(Order.return_transaction),
    #                                 joinedload(Order.commodity)\
    #                                 .joinedload(Commodity.wallet)\
    #                                 .joinedload(Wallet.user))\
    #                                 .filter(User.id == user_id)

    #         result = await session.execute(query)
    #         users_orders = result.scalars().all()
    #     return users_orders


order_eth_rep_link = OrderEthRepository()
