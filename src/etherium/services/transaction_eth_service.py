from src.etherium.services.transaction_abstract_service import (
    TransactionAbstractService,
)
from concurrent.futures import ThreadPoolExecutor
from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from eth_account import Account

from etherium_config.settings import w3_connection
from web3.exceptions import InvalidAddress

from src.etherium.repository.transaction_eth_repository import transaction_rep_link
from datetime import datetime


class TransactionETHService(TransactionAbstractService):
    async def send_eth_to_account(account_data):
        """
        {'address': '0xD870C92E01777ee585dbaA78aA8Ff1B2EFaBA65d',
        'value': '0.25',
        'current_wallet_id': '52'}

        address is address of receiver
        """
        print("Your account data is:")
        print(account_data)

        if account_data["address"] == "":
            result = {"result": "error", "error_text": "введіть адрессу отримувача"}

        elif account_data["value"] == "":
            result = {"result": "error", "error_text": "введіть сумму для транзакції"}
        else:
            try:
                await w3_connection.eth.get_balance(account_data["address"])

                receiver_address = account_data["address"]
                current_wallet_id = account_data["current_wallet_id"]
                curent_wallet = await WalletEtheriumService.return_wallet_per_id(
                    id=current_wallet_id
                )
                sender_adress = curent_wallet.address
                value = account_data["value"]

                curent_wallet = await WalletEtheriumService.return_wallet_per_id(
                    id=current_wallet_id
                )

                sender_private_key = curent_wallet.private_key
                account_obj = Account.from_key(sender_private_key)

                nonce = await w3_connection.eth.get_transaction_count(
                    account_obj.address, "pending"
                )
                chain_id = await w3_connection.eth.chain_id
                gas_price = await w3_connection.eth.gas_price

                transaction = {
                    "from": account_obj.address,
                    "chainId": chain_id,
                    "nonce": nonce,
                    "gas": 21000,
                    "gasPrice": gas_price * 4,
                    "value": w3_connection.to_wei(value, "ether"),
                    "to": receiver_address,
                }

                with ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        w3_connection.eth.account.sign_transaction,
                        transaction_dict=transaction,
                        private_key=sender_private_key,
                    )
                    # Ожидание результата и получение его
                    signed = future.result()

                tx_hash = await w3_connection.eth.send_raw_transaction(
                    signed.rawTransaction
                )

                print("--------")
                print(tx_hash)
                print("--------")

                tx = await w3_connection.eth.get_transaction(tx_hash)

                tx = await w3_connection.eth.get_transaction(tx_hash)
                # trx_block_number = tx.blockNumber

                print("transaction data")
                print(tx)
                print("block data")
                # ***посмотреть как мы сохраняем транзакции которые отправленны***

                transaction = await transaction_rep_link.save_transaction_in_db(
                    send_from=sender_adress,
                    send_to=receiver_address,
                    value=value,
                    txn_hash=tx_hash.hex(),
                    status="pending",
                )

                result = {
                    "result": "success",
                    "error_text": "",
                    "type": "sending_transaction",
                    "value": transaction.value,
                    "from": sender_adress,
                    "id": transaction.id,
                    "txn_hash": transaction.txn_hash,
                }

            except InvalidAddress:
                result = {
                    "result": "error",
                    "error_text": "помилка в адрессі отримувача",
                }
        return result

    async def return_all_transactions_per_wallet(wallet_adress):
        transactions = (
            await transaction_rep_link.return_all_transactions_per_waller_address(
                wallet_adress
            )
        )
        return transactions

    async def update_transaction(transaction_obj, transaction_new_data):
        await transaction_rep_link.update_transaction(
            transaction_obj, transaction_new_data
        )

    async def save_transaction(transaction_data_dict):
        from_web3_data_dict = {
            "date_time_transaction": transaction_data_dict["date_time_transaction"],
            "txn_fee": transaction_data_dict["txn_fee"],
        }
        await transaction_rep_link.save_transaction_in_db(
            send_from=transaction_data_dict["send_from"],
            send_to=transaction_data_dict["send_to"],
            value=w3_connection.from_wei(int(transaction_data_dict["value"]), "ether"),
            txn_hash=transaction_data_dict["txn_hash"],
            status=transaction_data_dict["status"],
            from_web3_data_dict=from_web3_data_dict,
        )

    async def create_or_update_transaction(transaction_obj):
        transaction_from_db = await transaction_rep_link.return_transaction_per_hash(
            transaction_obj.get("hash").hex()
        )

        match transaction_from_db:
            case None:
                # print('==============>>>>>>>>>>>>>>>>>>>This is new transaction!')
                transaction_full_data = await w3_connection.eth.get_transaction(
                    transaction_obj.get("hash").hex()
                )
                transaction_receipt = await w3_connection.eth.get_transaction_receipt(
                    transaction_obj.get("hash").hex()
                )
                value = w3_connection.from_wei(
                    int(transaction_obj.get("value")), "ether"
                )
                gas_used = transaction_full_data.get("gas")
                gas_price = transaction_full_data.get("gasPrice")
                txn_fee = gas_used * gas_price
                txn_fee_in_ether = w3_connection.from_wei((txn_fee), "ether")

                if transaction_receipt.get("status") == 1:
                    status = "success"
                elif transaction_receipt.get("status") == 0:
                    status = "fail"

                total_transaction_data = {
                    "send_from": transaction_obj.get("from"),
                    "send_to": transaction_obj.get("to"),
                    "value": value,
                    "txn_hash": transaction_obj.get("hash").hex(),
                    "status": status,
                    "from_web3_data_dict": {
                        # TODO datatime here
                        "date_time_transaction": datetime.now(),
                        "txn_fee": txn_fee_in_ether,
                    },
                }
                # print('=========total_transaction_data=========')
                # print(total_transaction_data)
                # print('========================================')
                transaction = await transaction_rep_link.save_transaction_in_db(
                    **total_transaction_data
                )
                # print('===========transaction===after===save===')
                # print(transaction)
                # print('========================================')
            case Transaction:  # noqa: F841
                # print('==============>>>>>>>>>>>>>>>>>>>this transaction need to update!')

                transaction_full_data = await w3_connection.eth.get_transaction(
                    transaction_from_db.txn_hash
                )
                transaction_receipt = await w3_connection.eth.get_transaction_receipt(
                    transaction_from_db.txn_hash
                )

                if transaction_receipt.get("status") == 1:
                    status = "success"
                elif transaction_receipt.get("status") == 0:
                    status = "fail"

                from_web3_data_dict = {}
                gas_used = transaction_full_data.get("gas")
                gas_price = transaction_full_data.get("gasPrice")
                txn_fee = gas_used * gas_price
                txn_fee_in_ether = w3_connection.from_wei((txn_fee), "ether")

                from_web3_data_dict = {
                    "date_time_transaction": datetime.now(),
                    "txn_fee": txn_fee_in_ether,
                    "status": status,
                }

                transaction = await transaction_rep_link.update_transaction(
                    transaction_from_db, from_web3_data_dict
                )

                # print('===============TRANSACTION=WAS=UPDATED=SUCCESSFULLY==================')
                # print(transaction)
                # print('=====================================================================')

        return transaction

    # TODO add schema in typing
    async def return_all_transactions_in_ssp_datatable(data_table_obj):
        transactions_result = (
            await transaction_rep_link.return_all_transactions_in_ssp_datatable(
                data_table_obj
            )
        )
        return transactions_result

    async def return_transaction_by_id(id):
        transaction = await transaction_rep_link.return_transaction_by_id(id)
        return transaction
