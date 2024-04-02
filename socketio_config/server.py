import socketio
from jose import JWTError, jwt
from redis_config.redis_config import add_user_to_chat_redis_hash,\
                                    add_seed_email_pair,\
                                    return_email_by_seed_and_delete,\
                                    delete_user_from_chat_redis_hash,\
                                    return_all_online_user
from propan import PropanApp, RabbitBroker
from propan.annotations import Logger
from propan.brokers.rabbit import RabbitExchange, RabbitQueue
from propan_config.router import add_to_message_query, queue_1, exch, Incoming, call, rabbit_router
# from propan_config.router import queue_1, exch, Incoming, call, rabbit_router
# from src.users.senders import add_to_message_query
from fastapi import Depends
from src.users.schemas import MessageFromChatModel
from src.users.services.services import save_new_message,\
                            return_last_messages,\
                            return_user_data_by_id

from src.wallets.data_adapters.db_services import send_eth_to_account
from datetime import datetime
from web3 import Web3
from web3.exceptions import InvalidAddress



SOCKETIO_PATH = "socket"
# While some tutorials use "*" as the cors_allowed_origins value, this is not safe practice.
CLIENT_URLS = ["http://localhost:8000", "ws://localhost:8000"]

# sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

url= 'amqp://guest:guest@localhost:5672'
# server = socketio.Server(client_manager=socketio.AsyncAioPikaManager(url))
client_manager = socketio.AsyncAioPikaManager(url)
server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*", client_manager=client_manager)
socket_app = socketio.ASGIApp(socketio_server=server, socketio_path='socket')
w3_connection = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/245f010db1cf410f87552fb31909a726'))

# socket_manager = socketio.AsyncAioPikaManager('amqp://')

# socket_app = socketio.ASGIApp(socketio_server=sio, socketio_path='socket')

SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"



# --------->>>>>messaging logic<<<<<<<<-------------------------------------------

class MessagingNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        # 1. проверка в селери тут ли находиться этот пользователь
        # 2. сохраненния данных о пользователе в REDIS
        # 3. добавление пользователя в комнату

        token = auth['token']
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        # users_online = await return_all_online_user()

        # await client_manager.emit('show_online_users', data=users_online, room=sid, namespace='/messaging')


        user_status = await add_user_to_chat_redis_hash(sid, email)
        await add_seed_email_pair(sid, email)
        await client_manager.enter_room(sid, room='chat_room', namespace='/messaging')
        
        # !--->>><<<---!
        users_online = await return_all_online_user()
        await client_manager.emit('show_online_users', data=users_online, room=sid, namespace='/messaging')


        if user_status['status'] == 'new':
            print('----user----is----new!!!---')
            await client_manager.emit('add_new_user_to_chat', {'data': user_status['user_data']}, room='chat_room', namespace='/messaging')



    async def on_disconnect(self, sid):
        # 1. удаление сведений о юзере в селери
        # 2. возвращение сведений в чат

        raw_email_list = await return_email_by_seed_and_delete(sid)
        email = raw_email_list[0].decode()
        leaved_user_data = await delete_user_from_chat_redis_hash(sid, email)
        await client_manager.leave_room(sid, room='chat_room', namespace='/messaging')
        if leaved_user_data['status'] == 'disconnected':
            await client_manager.emit('remove_user_from_chat', {'data': leaved_user_data}, room='chat_room', namespace='/messaging')
            


    async def on_send_message(self, sid, data):

        token = data['token']
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        data_obj = MessageFromChatModel(message=data['message'], email=email)

        if 'photo' in data:
            dt = datetime.now()
            ts = datetime.timestamp(dt)
            filename = email + '__' + str(ts)

            with open(f'media/external_storage/{filename}', 'wb') as f: 
                f.write(data['photo'])

            data_obj.photo = filename

        await save_new_message(data_obj)

    async def on_return_last_messages_from_chat(self, sid):

        last_messages = await return_last_messages()

        await client_manager.emit('receive_last_messages_from_chat', data=last_messages, room=sid, namespace='/messaging')


    async def on_get_other_user_data(self, sid, data):
        user_id = data['user_id']
        user_data = await return_user_data_by_id(user_id)
        print('-----users---data---is-----')
        await client_manager.emit('receive_other_user_data', data=user_data, room=sid, namespace='/messaging')



# show send message
async def return_saved_message(message):
    await  client_manager.emit('show_saved_message', data={'message': message}, room='chat_room', namespace='/messaging')




server.register_namespace(MessagingNamespace('/messaging'))


from src.wallets.data_adapters.db_services import return_wallets_per_user, create_wallet_for_user, import_wallet_for_user
from celery_config.config import monitoring_wallets_state_task, app

from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from src.users.services.user_service import UserService

# --------->>>>>wallets logic<<<<<<<<-------------------------------------------
class WalletProfileNamespace(socketio.AsyncNamespace):


    async def on_connect(self, sid, environ, auth):
        email = await UserService.return_email_by_token(token = auth['token'])
        all_users_wallets = await WalletEtheriumService.return_wallets_per_user_email(email = email)
        wallets_data = {'all_users_wallets': all_users_wallets}
        await client_manager.emit('return_list_of_user_wallets', \
                            data=wallets_data, \
                            room=sid, \
                            namespace='/profile_wallets')


    async def on_disconnect(self, sid):
        pass


    async def on_create_wallet(self, sid, data):
        new_wallet_data = {'token': data['token'], 'sid': sid}
        new_walet_dict = await WalletEtheriumService.create_wallet_for_user(new_wallet_data)
        await return_new_wallet(new_walet_dict)
        



    async def on_import_wallet(self, sid, data):
        # balance = 
        import_wallet_data = {'token': data['token'],
                              'private_key': data['private_key'],
                               'sid': sid}

        await WalletEtheriumService.import_wallet_for_user(import_wallet_data)


    async def on_send_transaction(self, sid, data):

        print('!!!')
        if data['address'] == '':
            error_data = {'error': 'введіть адрессу отримувача'}
            await client_manager.emit('transaction_error', data=error_data, room=sid, namespace='/profile_wallets')
        elif data['value'] == '':
            error_data = {'error': 'введіть сумму для транзакції'}
            await client_manager.emit('transaction_error', data=error_data, room=sid, namespace='/profile_wallets')

        try:
            w3_connection.eth.get_balance(data['address'])
            print('---sending data---')
            await send_eth_to_account(data)

        except InvalidAddress:
            error_data = {'error': 'адресса отримувача не валідна'}
            await client_manager.emit('transaction_error', data=error_data, room=sid, namespace='/profile_wallets')

        # print('========================')


async def return_new_wallet(message):
    print('===You want return this wallet in sockets===')
    print(message)
    print('============================================')
    sid = message.pop('sid')
    await  client_manager.emit('show_new_wallet', room=sid, data=message, namespace='/profile_wallets')



async def update_wallet_state(wallets_data, sid):
    await client_manager.emit('return_list_of_user_wallets', \
                                data=wallets_data, \
                                room=sid, \
                                namespace='/profile_wallets')


server.register_namespace(WalletProfileNamespace('/profile_wallets'))