
from etherium_config.settings import aiotherscan_client_executor
from src.etherium.services.transaction_eth_service import TransactionETHService
from datetime import datetime
from etherium_config.settings import w3_connection
import asyncio


class ETHScannerService():


    @aiotherscan_client_executor
    async def return_all_transactions_by_wallet(aiotherscan_client, wallet_data):

        transactions_list = await aiotherscan_client.account.normal_txs(address=wallet_data['current_wallet_adress'])

        transaction_dict = {}
        for transaction in transactions_list:

            if transaction['txreceipt_status'] == '1':
                status= 'success'
            elif transaction['txreceipt_status'] == '0':
                status= 'fail'

            transaction_dict[transaction['hash']] = {
                'from': w3_connection.to_checksum_address(transaction['from']),
                'send_to': w3_connection.to_checksum_address(transaction['to']),
                'value': transaction['value'],
                'txn_hash': transaction['hash'],
                'date_time_transaction': datetime.fromtimestamp(int(transaction['timeStamp'])),
                'txn_fee': w3_connection.from_wei(int(transaction['cumulativeGasUsed']), 'ether'),
                'status': status
            }


        await ETHScannerService.compare_current_transactions_with_saved(transaction_dict, wallet_data)
        

    @staticmethod
    async def compare_current_transactions_with_saved(transaction_dict, wallet_data):
        saved_transactions = await TransactionETHService.return_all_transactions_per_wallet(wallet_data['current_wallet_adress'], wallet_data['wallet_id'])
        print('--->>>saved transactions<<<---')
        print(saved_transactions)
        print('------------------------------')

        for transaction_obj in saved_transactions:
            if transaction_obj.txn_hash in transaction_dict and transaction_obj.status == 'pending':
                transaction_new_data = transaction_dict[transaction_obj.txn_hash]
                await TransactionETHService.update_transaction(transaction_obj, transaction_new_data)
                del transaction_dict[transaction_obj.txn_hash]
            elif transaction_obj.txn_hash in transaction_dict and transaction_obj.status != 'pending':
                del transaction_dict[transaction_obj.txn_hash]

        if len(transaction_dict) != 0:
            for txn_hash in transaction_dict:
                await TransactionETHService.save_transaction(transaction_dict[txn_hash])