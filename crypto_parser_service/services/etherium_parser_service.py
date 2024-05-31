import asyncio
import json

from web3 import Web3, AsyncWeb3
import httpx
import aiohttp

from src.etherium.services.transaction_eth_service import TransactionETHService
from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from propan_config.router import add_to_return_transaction_message_to_socket

from socketio_config.server import client_manager


class ETHParserService:
    '''
    Service class for parsing Ethereum blocks on the Sepolia network

    class Attrs:
        - web3_connection(Web3):  Connection instance using WebSockets for listening to new blocks.
        - web3_async_connection(AsyncWeb3): Connection instance using asynchronous HTTP for retrieving transaction data.
        - sender_message(str): Template message for sending notifications to the sender.
        - receiver_message(str): Template message for sending notifications to the receiver.
    '''
    web3_connection = Web3(Web3.WebsocketProvider("wss://sepolia.infura.io/ws/v3/245f010db1cf410f87552fb31909a726"))
    web3_async_connection = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider("https://sepolia.infura.io/v3/245f010db1cf410f87552fb31909a726"))
    sender_message = "Знято {} TRX з гаманця {}"
    receiver_message = "Отримано {} TRX з гаманця {}"

    async def parse_block(self) -> None:
        '''
            Parses the latest block on the Sepolia network.

            This function sets up a WebSocket connection with the Infura node,
            subscribes to new block events, and calls `handle_block`
            with the block number when a new block is detected. It also checks for
            the health of the CryptoWallet service to ensure proper operation.
        '''

        
        from celery_config.tasks import handle_block

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect("wss://sepolia.infura.io/ws/v3/245f010db1cf410f87552fb31909a726") as connection:
                dictionary = {"id": 1, "method": "eth_subscribe", "params": ["newHeads"]}
                message = json.dumps(dictionary)
                await connection.send_str(message)
                await connection.receive()
                data = None       
                while True:
                    # wait data from connecrion
                    raw_data = await asyncio.wait_for(connection.receive(), timeout=60)
                    data = json.loads(raw_data.data)
                    block_number_hex = data['params']['result']['number']
                    block_number = int(block_number_hex, 16)
                    # logs for dev
                    print('======DATA======')
                    print(f"Block Number: {block_number}")
                    print('================')
                    try:
                        # check if cryptowallet run
                        await self.check_if_crypto_wallet_run()
                        # return block_number
                        handle_block.delay(block_number)

                    except Exception as exc:
                        print('Exception in parsing')
                        print(exc)
                        break

    @staticmethod
    async def check_if_crypto_wallet_run() -> None:
        """
        Checks if the CryptoWallet service is running.

        This function is used within the `parse_latest_block` loop to ensure CryptoWallet is
        operational before processing the block. If CryptoWallet is not reachable, an exception
        can be raised to stop the loop.
        """
        async with httpx.AsyncClient() as client:
            fastapi_url = "http://localhost:8000/health"
            await client.get(fastapi_url)
    

    @classmethod
    async def handle_block(cls, block_number: int) -> None:
        """
        Processes a block and extracts relevant data for transaction notifications.

        This method fetches all transactions from a given block (`block_number`) and retrieves 
        registered wallet addresses from the database. It then iterates through each address 
        associated with the transactions (senders and receivers) to identify any matches 
        with registered wallets.

        - For matching addresses, it gathers data for notification purposes (stored in 
        dictionaries like `transaction_notification_from` and `transaction_notification_to`).
        - It also collects the complete transaction data for relevant transactions and stores 
        them in a set (`transactions`).
        - The `transactions` set is passed to a separate repository for updating or creating 
        transactions in the database.
        - Finally, the method send dictionaries of transactions data in send_notification method.

        Args:
            - block_number(int): number of parsed block
        """



        block_data = await cls.web3_async_connection.eth.get_block(block_number, full_transactions=True)

        transactions_set = set()
        transaction_notification_from = {}
        transaction_notification_to = {}

        wallets_addresses_dict = await WalletEtheriumService.return_all_wallets_addresses()

        for transaction in block_data.transactions:
 
            if transaction.get('from') in wallets_addresses_dict:
                transactions_set.add(transaction)
                value = cls.web3_async_connection.to_wei(transaction.get('value'), 'ether')
                transaction_notification_from[transaction.get('hash').hex()] = {'value': value, 
                                                                                'user_id': wallets_addresses_dict[transaction.get('from')],
                                                                                'wallet': transaction.get('from')}
            if transaction.get('to') in wallets_addresses_dict:
                transactions_set.add(transaction)
                value = cls.web3_async_connection.to_wei(transaction.get('value'), 'ether')
                transaction_notification_to[transaction.get('hash').hex()] = {'summ': value, 
                                                                                'user_id': wallets_addresses_dict[transaction.get('to')],
                                                                                'wallet': transaction.get('to')}


        for transaction in transactions_set:
            saved_transaction = await TransactionETHService.create_or_update_transaction(transaction)
            # print(saved_transaction)
            # send notification, if transaction was send from one of the wallets
            if saved_transaction.txn_hash in transaction_notification_from:
                notification_dict = {'type': 'from',
                                     'txn_hash': saved_transaction.txn_hash,
                                     'summ': saved_transaction.value + saved_transaction.txn_fee,
                                     'user_id': transaction_notification_from[saved_transaction.txn_hash]['user_id'],
                                     'wallet': transaction_notification_from[saved_transaction.txn_hash]['wallet']}
                await cls.send_notification(notification_dict)

            # send notification, if transaction was received in one of the wallets
            if saved_transaction.txn_hash in transaction_notification_to:
                notification_dict = {'type': 'to',
                                     'txn_hash': saved_transaction.txn_hash,
                                     'summ': saved_transaction.value,
                                     'user_id': transaction_notification_to[saved_transaction.txn_hash]['user_id'],
                                     'wallet': transaction_notification_to[saved_transaction.txn_hash]['wallet']}
                await cls.send_notification(notification_dict)

        print('--------->your transactions set is:<---------')
        # pprint.pprint(transactions_set)
        # print('transaction_notification_from')
        print(transaction_notification_from)
        print('transaction_notification_to')
        print(transaction_notification_to)
        print(f'There was: --->>>{block_number}<<<---')
        print('--------------------------------------')




    @classmethod
    async def send_notification(cls, notification_data:dict) -> None:

        """
            Sends a notification about a transaction (sent or received) 
            associated with a user's wallet in CrypoWallet.

            This method utilizes sockets for notification delivery.

            Args:
                notification_data (dict): Dictionary containing transaction details,
                    including 'type' ('from' or 'to'), 'summ' (transaction amount), 
                    'wallet' (wallet address), and 'user_id' (user identifier).
        """

        print('NOTIFAICATION---DATA--------->>>')
        
        if notification_data['type'] == 'from':
            message = cls.sender_message.format(notification_data['summ'], notification_data['wallet'])
            print('RECEIVER---MESSAGE-------->>>')
            print('--->notification_data-----')
            wallet_in_db = await WalletEtheriumService.return_wallet_per_address(notification_data['wallet'])
            updated_balance = await WalletEtheriumService.update_and_return_ballance_state(wallet_in_db)
            # print('----updated---ballance--')
            # print(updated_balance)
            # print('***')
            socket_notification_dict = {
                'message': message,
                'user_id': notification_data['user_id'],
                'wallet_id': wallet_in_db.id,
                'new_wallet_ballance': float(updated_balance)
            }
            print(message)
            room_number = notification_data['user_id']

            await client_manager.emit('receive_data_from_parser', \
                                data=socket_notification_dict, \
                                room=f'room_{room_number}', \
                                namespace='/profile_wallets')



            

        elif notification_data['type'] == 'to':
            message = cls.receiver_message.format(notification_data['summ'], notification_data['wallet'])
            print('RECEIVER---MESSAGE-------->>>')
            print('--->notification_data-----')
            print(notification_data)
            wallet_in_db = await WalletEtheriumService.return_wallet_per_address(notification_data['wallet'])
            updated_balance = await WalletEtheriumService.update_and_return_ballance_state(wallet_in_db)
            # print('----updated---ballance--')
            # print(updated_balance)
            # print('***')
            socket_notification_dict = {
                'message': message,
                'user_id': notification_data['user_id'],
                'wallet_id': wallet_in_db.id,
                'new_wallet_ballance': float(updated_balance)
            }
            print(message)
            room_number = notification_data['user_id']
            await client_manager.emit('receive_data_from_parser', \
                                data=socket_notification_dict, \
                                room=f'room_{room_number}', \
                                namespace='/profile_wallets')
        

