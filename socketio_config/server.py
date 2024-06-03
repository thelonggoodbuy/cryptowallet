import socketio
from jose import JWTError, jwt
# from redis_config.redis_config import add_user_to_chat_redis_hash,\
#                                     add_seed_email_pair,\
#                                     return_email_by_seed_and_delete,\
#                                     delete_user_from_chat_redis_hash,\
#                                     return_all_online_user
from redis_config.services.redis_user_service import redis_user_service
from redis_config.services.redis_parser_service import redis_parser_service
from propan import PropanApp, RabbitBroker
from propan.annotations import Logger
from propan.brokers.rabbit import RabbitExchange, RabbitQueue
from propan_config.router import add_to_message_query, queue_1, exch, Incoming, call, rabbit_router, add_to_get_all_transcations_queue
from fastapi import Depends
from src.users.schemas import MessageFromChatModel
from src.orders.services.commodity_eth_service import CommodityEthService

# from src.etherium.services.transaction_eth_service import TransTransactionETHService
from datetime import datetime
from web3 import Web3
from web3.exceptions import InvalidAddress
from src.users.services.user_service import UserService
from src.users.services.message_service import MessageService

from etherium_config.settings import w3_connection


SOCKETIO_PATH = "socket"
CLIENT_URLS = ["http://localhost:8000", "ws://localhost:8000"]

url= 'amqp://guest:guest@localhost:5672'

client_manager = socketio.AsyncAioPikaManager(url)
server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*", client_manager=client_manager)
socket_app = socketio.ASGIApp(socketio_server=server, socketio_path='socket')
# w3_connection = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/245f010db1cf410f87552fb31909a726'))

# socket_manager = socketio.AsyncAioPikaManager('amqp://')

# socket_app = socketio.ASGIApp(socketio_server=sio, socketio_path='socket')

SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"




# --------->>>>>messaging logic<<<<<<<<-------------------------------------------

class MessagingNamespace(socketio.AsyncNamespace):


    async def on_connect(self, sid, environ, auth):
        email = await UserService.return_email_by_token(token = auth['token'])
        user_status = await redis_user_service.add_user_to_chat_redis_hash(sid, email)
        await redis_user_service.add_seed_email_pair(sid, email)
        await client_manager.enter_room(sid, room='chat_room', namespace='/messaging')
        users_online = await redis_user_service.return_all_online_user()

        await client_manager.emit('show_online_users', data=users_online, room=sid, namespace='/messaging')
        if user_status['status'] == 'new':
            await client_manager.emit('add_new_user_to_chat', {'data': user_status['user_data']}, room='chat_room', namespace='/messaging')



    async def on_disconnect(self, sid):
        raw_email_list = await redis_user_service.return_email_by_seed_and_delete(sid)
        email = raw_email_list[0].decode()
        leaved_user_data = await redis_user_service.delete_user_from_chat_redis_hash(sid, email)
        await client_manager.leave_room(sid, room='chat_room', namespace='/messaging')
        if leaved_user_data['status'] == 'disconnected':
            await client_manager.emit('remove_user_from_chat', {'data': leaved_user_data}, room='chat_room', namespace='/messaging')
            


    async def on_send_message(self, sid, data):
        data['email'] = await UserService.return_email_by_token(token = data['token'])
        data_obj = MessageFromChatModel(**data)
        await MessageService.save_new_message(data_obj)


    async def on_return_last_messages_from_chat(self, sid):
        last_messages = await MessageService.return_last_messages()
        await client_manager.emit('receive_last_messages_from_chat', data=last_messages, room=sid, namespace='/messaging')


    async def on_get_other_user_data(self, sid, data):
        user_id = data['user_id']
        user_data = await UserService.return_user_data_by_id(user_id)
        await client_manager.emit('receive_other_user_data', data=user_data, room=sid, namespace='/messaging')



async def return_saved_message(message):
    await  client_manager.emit('show_saved_message', data={'message': message}, room='chat_room', namespace='/messaging')




server.register_namespace(MessagingNamespace('/messaging'))


# =====================================================================================
# =============================Waller namespace========================================
# =====================================================================================

from src.wallets.services.wallet_etherium_service import WalletEtheriumService

# from celery_config.config import monitoring_wallets_state_task, app

from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from src.users.services.user_service import UserService
from src.etherium.services.transaction_eth_service import TransactionETHService
from etherium_config.services.eth_parser import eth_parser_service


class WalletProfileNamespace(socketio.AsyncNamespace):

    sid_room_pairs = {}


    async def on_connect(self, sid, environ, auth):
        email = await UserService.return_email_by_token(token = auth['token'])
        user = await UserService.return_user_per_email(email)
        all_users_wallets = await WalletEtheriumService.return_wallets_per_user_email(email = email)
        wallets_data = {'all_users_wallets': all_users_wallets}


        room = f'room_{user.id}'
        self.sid_room_pairs[sid] = room
        
        await client_manager.enter_room(sid, namespace='/profile_wallets', room=room)
        print(f'-----you---room----is:*** {room}')

        await client_manager.emit('return_list_of_user_wallets', \
                            data=wallets_data, \
                            room=sid, \
                            namespace='/profile_wallets')
        
        await eth_parser_service.add_user_wallets_to_parser(sid, all_users_wallets, user.id)



    async def on_disconnect(self, sid):
        await eth_parser_service.delete_user_from_parser(sid)



    async def on_create_wallet(self, sid, data):
        # TODO изменить работу с комнатой в вызываемых в послдствии сервисах. все что связано с профилями
        new_wallet_data = {'token': data['token'], 'room': self.sid_room_pairs[sid]}
        new_walet_dict = await WalletEtheriumService.create_wallet_for_user(new_wallet_data)
        await return_new_wallet(new_walet_dict)
        


    async def on_import_wallet(self, sid, data):
        # TODO изменить работу с комнатой в вызываемых в послдствии сервисах. все что связано с профилями

        import_wallet_data = {'token': data['token'],
                              'private_key': data['private_key'],
                               'room': self.sid_room_pairs[sid]}
        await WalletEtheriumService.import_wallet_for_user(import_wallet_data)


    async def on_send_transaction(self, sid, data):
        user_id = await WalletEtheriumService.return_user_id_by_wallet_id(data['current_wallet_id'])
        room = f'room_{user_id}'
        transaction_data = await TransactionETHService.send_eth_to_account(data)
        await client_manager.emit('transaction_sending_result', data=transaction_data, room=room, namespace='/profile_wallets')


    async def on_get_transactions_per_wallet(self, sid, data):
        # TODO изменить работу с комнатой в вызываемых в послдствии сервисах. все что связано с профилями
        message = {'data': data, 'sid': sid}
        await add_to_get_all_transcations_queue(message)

        
    # async def on_update_concrete_wallet_per_id(self, sid, data):






async def return_new_wallet(message):
    # TODO изменить работу с комнатой в вызываемых в послдствии сервисах. все что связано с профилями
    room = message.pop('room')
    await  client_manager.emit('show_new_wallet', room=room, data=message, namespace='/profile_wallets')



async def update_wallet_state(wallets_data, sid):
    # TODO изменить работу с комнатой в вызываемых в послдствии сервисах. все что связано с профилями
    await client_manager.emit('return_list_of_user_wallets', \
                                data=wallets_data, \
                                room=sid, \
                                namespace='/profile_wallets')
    


async def return_all_transactions_per_wallet(transaction_data, sid):
    print('transaction_data is: ')
    print(transaction_data)
    await client_manager.emit('return_all_transactions_per_wallet', \
                            data=transaction_data, \
                            room=sid,\
                            namespace='/profile_wallets')
    




server.register_namespace(WalletProfileNamespace('/profile_wallets'))






class IBayNamespace(socketio.AsyncNamespace):

    sid_room_pairs = {}


    async def on_connect(self, sid, environ, auth):
        email = await UserService.return_email_by_token(token = auth['token'])
        user = await UserService.return_user_per_email(email)

        room = f'room_ibay_{user.id}'
        self.sid_room_pairs[sid] = room
        
        await client_manager.enter_room(sid, namespace='/ibay', room=room)
        print(f'-----you---room----is:*** {room}')


    async def on_disconnect(self, sid):
        # await eth_parser_service.delete_user_from_parser(sid)
        pass



    async def on_create_announcement(self, sid, data):
        response = await CommodityEthService.save_commodity(data['sending_data'])

        if 'errors' in response:
            room = self.sid_room_pairs[sid]
            await client_manager.emit('validation_error', \
                            room=room,\
                            data=response, \
                            namespace='/ibay')
        else:
            await client_manager.emit('add_new_commodity', \
                                data=response, \
                                namespace='/ibay')
        



server.register_namespace(IBayNamespace('/ibay'))
