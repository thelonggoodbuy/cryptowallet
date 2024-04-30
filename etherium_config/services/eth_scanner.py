
from etherium_config.settings import aiotherscan_client_executor
from src.etherium.services.transaction_eth_service import TransactionETHService
from datetime import datetime
from etherium_config.settings import w3_connection
import asyncio
from propan_config.router import add_to_return_to_socketio_all_transcations_queue


 

class ETHScannerService():


    @aiotherscan_client_executor
    async def return_all_transactions_by_wallet(aiotherscan_client, wallet_data, sid):

        transactions_list = await aiotherscan_client.account.normal_txs(address=wallet_data['current_wallet_adress'])
        transaction_dict = {}
        for transaction in transactions_list:

            if transaction['txreceipt_status'] == '1':
                status= 'success'
            elif transaction['txreceipt_status'] == '0':
                status= 'fail'

            transaction_dict[transaction['hash']] = {
                'send_from': w3_connection.to_checksum_address(transaction['from']),
                'send_to': w3_connection.to_checksum_address(transaction['to']),
                'value': transaction['value'],
                'txn_hash': transaction['hash'],
                'date_time_transaction': datetime.fromtimestamp(int(transaction['timeStamp'])),
                'txn_fee': w3_connection.from_wei(int(transaction['cumulativeGasUsed']), 'ether'),
                'status': status
            }


        await ETHScannerService.compare_current_transactions_with_saved(transaction_dict, wallet_data)
        saved_transactions_list = await TransactionETHService.return_all_transactions_per_wallet(wallet_data['current_wallet_adress'])
        formated_transaction_list = await ETHScannerService.format_all_transactions_per_wallet(saved_transactions_list)
        message = {'formated_transaction_list': formated_transaction_list, 'sid': sid}
        await add_to_return_to_socketio_all_transcations_queue(message)


    @aiotherscan_client_executor
    async def synchronize_transaction_state_for_wallet(aiotherscan_client, wallet_data):
        transactions_list = await aiotherscan_client.account.normal_txs(address=wallet_data['current_wallet_adress'])
        transaction_dict = {}
        for transaction in transactions_list:

            if transaction['txreceipt_status'] == '1':
                status= 'success'
            elif transaction['txreceipt_status'] == '0':
                status= 'fail'

            transaction_dict[transaction['hash']] = {
                'send_from': w3_connection.to_checksum_address(transaction['from']),
                'send_to': w3_connection.to_checksum_address(transaction['to']),
                'value': transaction['value'],
                'txn_hash': transaction['hash'],
                'date_time_transaction': datetime.fromtimestamp(int(transaction['timeStamp'])),
                'txn_fee': w3_connection.from_wei(int(transaction['cumulativeGasUsed']), 'ether'),
                'status': status
            }
        await ETHScannerService.compare_current_transactions_with_saved(transaction_dict, wallet_data)
        # saved_transactions_list = await TransactionETHService.return_all_transactions_per_wallet(wallet_data['current_wallet_adress'])


        

    @staticmethod
    async def compare_current_transactions_with_saved(transaction_dict, wallet_data):
        saved_transactions = await TransactionETHService.return_all_transactions_per_wallet(wallet_data['current_wallet_adress'])
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


    
    @staticmethod
    async def format_all_transactions_per_wallet(saved_transactions_list):
        formated_transaction_list = []
        for transaction in saved_transactions_list:
            transaction_dict = {}
            transaction_dict['id'] = transaction.id
            transaction_dict['txn_hash'] = transaction.txn_hash
            transaction_dict['send_from'] = transaction.send_from
            transaction_dict['send_to'] = transaction.send_to
            transaction_dict['value'] = transaction.value
            transaction_dict['age'] = transaction.date_time_transaction
            transaction_dict['txn_fee'] = transaction.txn_fee
            transaction_dict['status'] = transaction.status.value

            formated_transaction_list.append(transaction_dict)

        return formated_transaction_list
    
