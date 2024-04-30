from redis_config.services.redis_parser_service import  redis_parser_service
import asyncio
from etherium_config.settings import w3_connection
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor
from src.etherium.services.transaction_eth_service import TransactionETHService




class ETHParserService():
    

    async def add_user_wallets_to_parser(self, sid, all_users_wallets, user_id):
        parser_status = await redis_parser_service.add_user_to_wallets_online(sid, all_users_wallets, user_id)



    async def delete_user_from_parser(self, sid):
        await redis_parser_service.delete_user_from_wallets_online(sid)


    async def update_transactions_from_parser(self, new_or_updated_transactions, send_to, send_from):

        message_set = set()

        for transaction_hash in new_or_updated_transactions:
            transaction_obj = await TransactionETHService.create_or_update_transaction(transaction_hash)

            try:
                receiver_wallet_address = send_to[transaction_hash]
                sid_list = redis_parser_service.return_list_of_sids_per_address(receiver_wallet_address)
                message_dict = {'sid_list': sid_list, 
                                'type': 'receive',
                                'account': transaction_obj.send_to,
                                'value': transaction_obj.value,
                                'status': transaction_obj.stutus,
                                'transaction_hash': transaction_obj.txn_hash}
                message_set.add(message_dict)

            except KeyError:
                pass

            try:
                sender_wallet_address = send_from[transaction_hash]
                sid_list = redis_parser_service.return_list_of_sids_per_address(sender_wallet_address)
                message_dict = {'sid_list': sid_list, 
                                'type': 'sending',
                                'account': transaction_obj.send_from,
                                'value': transaction_obj.value,
                                'status': transaction_obj.stutus,
                                'transaction_hash': transaction_obj.txn_hash}
                message_set.add(message_dict)

            except KeyError:
                pass

        
        print('Messages====before=====RabbitMQ')
        print(message_set)
        print('===============================')



eth_parser_service = ETHParserService()
