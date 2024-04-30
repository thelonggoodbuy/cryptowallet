from sqlalchemy.ext.asyncio import async_sessionmaker
from db_config.database import engine
from sqlalchemy import select

from src.etherium.models import Transaction
from src.wallets.models import Wallet
from sqlalchemy.orm import selectinload, contains_eager
from etherium_config.settings import w3_connection
from sqlalchemy import desc





class TransactionETHRepository():

    async def save_transaction_in_db(self,
                                     send_from,
                                     send_to,
                                     value,
                                     txn_hash,
                                     status,
                                     from_web3_data_dict = None):
        # print('===!!!===')
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            # print('===4===')
            transaction = Transaction(
                send_from=send_from,
                send_to=send_to,
                value=value,
                txn_hash=txn_hash,
                status=status
            )
            print('===5===')
            print(from_web3_data_dict)
            print('===5.1===')

            if from_web3_data_dict:
                for transaction_attribute in from_web3_data_dict:
                    setattr(transaction,\
                            transaction_attribute,\
                            from_web3_data_dict[transaction_attribute])

            session.add(transaction)
            await session.commit()

        return transaction
    

    async def return_all_transactions_per_waller_address(self, wallet_number):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        print('***')
        print(wallet_number)
        print('***')
        async with async_session() as session:
            query = select(Transaction)\
                    .filter((Transaction.send_from == wallet_number) | (Transaction.send_to == wallet_number))\
                    .order_by(desc(Transaction.id))

            transactions_data = await session.execute(query)
            transactions = transactions_data.scalars().unique().all()
        return transactions


    async def update_transaction(self, transaction_obj, transaction_new_data):

        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            # print('***')
            # print('transaction object')
            # print(transaction_obj)
            # print('transaction_new_data')
            # print(transaction_new_data)
            # print('***')
            transaction_obj.date_time_transaction = transaction_new_data['date_time_transaction']
            transaction_obj.txn_fee = transaction_new_data['txn_fee']
            transaction_obj.status = transaction_new_data['status']
            # print('===2===')
            session.add(transaction_obj)
            # print('===3===')
            await session.commit()
            # print('===4===')
        return transaction_obj

    async def return_transaction_per_hash(self, transaction_hash):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Transaction).filter(Transaction.txn_hash == transaction_hash)
            result = await session.execute(query)
            transaction = result.scalars().first()
        return transaction
    
transaction_rep_link = TransactionETHRepository()