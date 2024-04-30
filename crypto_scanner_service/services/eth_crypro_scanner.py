
from src.etherium.services.transaction_eth_service import TransactionETHService
from datetime import datetime
from propan_config.router import add_to_return_to_socketio_all_transcations_queue
from crypto_scanner_service.services.abstract_crypto_scanner import AbstractCryproScanner

from web3 import Web3, AsyncWeb3
from web3.eth import AsyncEth

from aioetherscan import Client as AiotherscanClient
from aiohttp_retry import ExponentialRetry
from asyncio_throttle import Throttler



class EtheriumCryproScanner(AbstractCryproScanner):

    """
    Сlass for asynchronously scanning transaction states in concrete etherium wallets,
    synchronizing them with the state in the database, and formatting the results.
    """

    def __init__(self):

        """
        initialisation of web3 connection
        """
        self.w3_connection = Web3(AsyncWeb3.AsyncHTTPProvider("https://sepolia.infura.io/v3/245f010db1cf410f87552fb31909a726"), 
                        modules={'eth': (AsyncEth,)}, 
                        middlewares=[])
       
    
    async def return_all_transactions_by_wallet(self, 
                                                wallet_data: dict, 
                                                sid: str) -> None:

        """
        Retrieves all transactions associated with a specific etherium wallet, 
        potentially from an external source (blockchain).

        Args:
            wallet_data(dict): dictionary with keys:
                - wallet_id(str): Id of wallet, content in DB
                - current_wallet_adress(str): address in etherium web3

            sid(str): session data for sockets
        """


        throttler = Throttler(rate_limit=1, period=6.0)
        retry_options = ExponentialRetry(attempts=2)
        aiotherscan_client = AiotherscanClient('1A17HIRIZMJXY6JMPQ15BEQQYJJT4CQFPJ', network="sepolia", throttler=throttler, retry_options=retry_options)

        transactions_list = await aiotherscan_client.account.normal_txs(address=wallet_data['current_wallet_adress'])
        transaction_dict = {}
        for transaction in transactions_list:

            if transaction['txreceipt_status'] == '1':
                status= 'success'
            elif transaction['txreceipt_status'] == '0':
                status= 'fail'

            transaction_dict[transaction['hash']] = {
                'send_from': self.w3_connection.to_checksum_address(transaction['from']),
                'send_to': self.w3_connection.to_checksum_address(transaction['to']),
                'value': transaction['value'],
                'txn_hash': transaction['hash'],
                'date_time_transaction': datetime.fromtimestamp(int(transaction['timeStamp'])),
                'txn_fee': self.w3_connection.from_wei(int(transaction['cumulativeGasUsed']), 'ether'),
                'status': status
            }

        await self.compare_current_transactions_with_saved(transaction_dict, wallet_data)
        saved_transactions_list = await TransactionETHService.return_all_transactions_per_wallet(wallet_data['current_wallet_adress'])
        formated_transaction_list = await self.format_all_transactions_per_wallet(saved_transactions_list)
        message = {'formated_transaction_list': formated_transaction_list, 'sid': sid}
        await add_to_return_to_socketio_all_transcations_queue(message)
        await aiotherscan_client.close()



    async def synchronize_transaction_state_for_wallet(self, 
                                                       wallet_data: dict) -> None:
        """
        Synchronizes the transaction state between the external source (etherium blockchain)
        and the database for a specific wallet. This method may involve identifying 
        new transactions or updating existing ones.

        Args:
            wallet_data(dict): dictionary with key "current_wallet_adress", what content address
                of wallet in etherium web and in db.
        """

        throttler = Throttler(rate_limit=1, period=6.0)
        retry_options = ExponentialRetry(attempts=2)
        aiotherscan_client = AiotherscanClient('1A17HIRIZMJXY6JMPQ15BEQQYJJT4CQFPJ', network="sepolia", throttler=throttler, retry_options=retry_options)

        transactions_list = await aiotherscan_client.account.normal_txs(address=wallet_data['current_wallet_adress'])
        transaction_dict = {}
        for transaction in transactions_list:

            if transaction['txreceipt_status'] == '1':
                status= 'success'
            elif transaction['txreceipt_status'] == '0':
                status= 'fail'

            transaction_dict[transaction['hash']] = {
                'send_from': self.w3_connection.to_checksum_address(transaction['from']),
                'send_to': self.w3_connection.to_checksum_address(transaction['to']),
                'value': transaction['value'],
                'txn_hash': transaction['hash'],
                'date_time_transaction': datetime.fromtimestamp(int(transaction['timeStamp'])),
                'txn_fee': self.w3_connection.from_wei(int(transaction['cumulativeGasUsed']), 'ether'),
                'status': status
            }
        await self.compare_current_transactions_with_saved(transaction_dict, wallet_data)
        await aiotherscan_client.close()

        

    @staticmethod
    async def compare_current_transactions_with_saved(transaction_dict: dict,
                                                        wallet_data: dict) -> None:
        """
        Compares the current transactions retrieved 
        (potentially in `synchronize_transaction_state_for_wallet`)
        with the ones stored in the database for a 
        specific wallet.

         Args:
            transaction_dict(dict): dictionary of transactions from etherium web. Key
                is a hash of transaction, value - is a dictionary of needfull transactions data
            wallet_data(dict): dictionary with key "current_wallet_adress", what content address
                of wallet in etherium web and in db.
        """
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
    async def format_all_transactions_per_wallet(saved_transactions_list:list) -> list:
        """
        Formats all transactions (potentially including identified differences) 
        in a specific way for presentation or further processing(potentially for
        message broker).

        Args:
            saved_transactions_list(list): list of transactions from db
        """
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
    



etherium_crypro_scanner = EtheriumCryproScanner()
