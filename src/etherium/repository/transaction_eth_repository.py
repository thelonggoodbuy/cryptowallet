from sqlalchemy.ext.asyncio import async_sessionmaker
from db_config.database import engine
from sqlalchemy import select
import copy
from src.etherium.models import Transaction
from sqlalchemy import desc, asc

from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from sqlalchemy import func
from datetime import datetime


class TransactionETHRepository:
    async def save_transaction_in_db(
        self, send_from, send_to, value, txn_hash, status, from_web3_data_dict=None
    ):
        # print('===!!!===')
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            transaction = Transaction(
                send_from=send_from,
                send_to=send_to,
                value=value,
                txn_hash=txn_hash,
                status=status,
            )
            print("===5===")
            print(from_web3_data_dict)
            print("===5.1===")

            if from_web3_data_dict:
                for transaction_attribute in from_web3_data_dict:
                    setattr(
                        transaction,
                        transaction_attribute,
                        from_web3_data_dict[transaction_attribute],
                    )

            session.add(transaction)
            await session.commit()

        return transaction

    async def return_all_transactions_per_waller_address(self, wallet_number):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        print("***")
        print(wallet_number)
        print("***")
        async with async_session() as session:
            query = (
                select(Transaction)
                .filter(
                    (Transaction.send_from == wallet_number)
                    | (Transaction.send_to == wallet_number)
                )
                .order_by(desc(Transaction.id))
            )

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
            transaction_obj.date_time_transaction = transaction_new_data[
                "date_time_transaction"
            ]
            transaction_obj.txn_fee = transaction_new_data["txn_fee"]
            transaction_obj.status = transaction_new_data["status"]
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

    # TODO add schema in typing
    async def return_all_transactions_in_ssp_datatable(self, data_table_obj):
        columns_dictionary = {
            "4": "date_time_transaction",
            "5": "txn_fee",
            "6": "status",
        }
        print("----->repository<-----")
        print(data_table_obj)
        wallet_address = (
            await WalletEtheriumService.return_wallet_per_id(data_table_obj.wallet_id)
        ).address
        if data_table_obj.order_column:
            order_column_name = columns_dictionary.get(str(data_table_obj.order_column))
        else:
            order_column_name = "id"

        if order_column_name == "id":
            order_direction = desc
        else:
            order_direction = desc if data_table_obj.order_dir == "desc" else asc

        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            print(order_direction)
            print(order_column_name)
            query = (
                select(Transaction)
                .filter(
                    (Transaction.send_from == wallet_address)
                    | (Transaction.send_to == wallet_address)
                )
                .order_by(order_direction(getattr(Transaction, order_column_name)))
                .slice(
                    data_table_obj.start, data_table_obj.start + data_table_obj.length
                )
            )

            transactions_data = await session.execute(query)
            transactions = transactions_data.scalars().unique().all()

            total_transactions_counter = await session.execute(
                select(func.count(Transaction.id)).filter(
                    (Transaction.send_from == wallet_address)
                    | (Transaction.send_to == wallet_address)
                )
            )
            total_transactions = total_transactions_counter.scalar()

        print("--->transactions<---")
        print(transactions)
        for transaction in transactions:
            print(transaction.txn_hash)
        print("--------------------")
        result_list = []
        transaction_dict = {}
        for transaction in transactions:
            new_transaction_list = copy.deepcopy(transaction_dict)
            new_transaction_list["txn_hash"] = transaction.txn_hash
            new_transaction_list["from"] = transaction.send_from
            new_transaction_list["to"] = transaction.send_to
            # float_value = float(transaction.value)
            # new_transaction_list['value'] = f"{float(transaction.value):.18f}"
            new_transaction_list["value"] = float(transaction.value)
            if transaction.date_time_transaction:
                # new_transaction_list['age'] = transaction.date_time_transaction.isoformat()
                new_transaction_list["age"] = await self.format_time_difference(
                    transaction.date_time_transaction
                )
            else:
                new_transaction_list["age"] = None
            if transaction.txn_fee:
                # new_transaction_list['txn_fee'] = float(transaction.txn_fee)
                txn_fee_format_value = f"{float(transaction.txn_fee):.18f}".rstrip(
                    "0"
                ).rstrip(".")
                new_transaction_list["txn_fee"] = txn_fee_format_value
            else:
                new_transaction_list["txn_fee"] = "Block not completed"
            new_transaction_list["status"] = transaction.status.value
            result_list.append(new_transaction_list)

        db_result_dict = {}
        db_result_dict["total_transactions_counter"] = total_transactions
        db_result_dict["result_list"] = result_list

        return db_result_dict

    async def format_time_difference(self, transaction_time: datetime) -> str:
        now = datetime.now()
        time_difference = now - transaction_time

        seconds = time_difference.total_seconds()
        if seconds < 60:
            return f"{int(seconds)} seconds ago"

        minutes = seconds / 60
        if minutes < 60:
            return f"{int(minutes)} minutes ago"

        hours = minutes / 60
        if hours < 24:
            return f"{int(hours)} hours ago"

        days = hours / 24
        if days < 30:
            return f"{int(days)} days ago"

        months = days / 30
        if months < 12:
            return f"{int(months)} months ago"

        years = months / 12
        return f"{int(years)} years ago"

    async def return_transaction_by_id(self, id):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Transaction).filter(Transaction.id == id)
            result = await session.execute(query)
            transaction = result.scalars().first()
        return transaction


transaction_rep_link = TransactionETHRepository()
