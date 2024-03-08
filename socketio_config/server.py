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
from fastapi import Depends
from src.users.pydantic_models import MessageFromChatModel
from src.users.services import save_new_message, return_last_messages
from datetime import datetime



SOCKETIO_PATH = "socket"
# While some tutorials use "*" as the cors_allowed_origins value, this is not safe practice.
CLIENT_URLS = ["http://localhost:8000", "ws://localhost:8000"]

# sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

url= 'amqp://guest:guest@localhost:5672'
# server = socketio.Server(client_manager=socketio.AsyncAioPikaManager(url))
client_manager = socketio.AsyncAioPikaManager(url)
server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*", client_manager=client_manager)
socket_app = socketio.ASGIApp(socketio_server=server, socketio_path='socket')
# socket_manager = socketio.AsyncAioPikaManager('amqp://')

# socket_app = socketio.ASGIApp(socketio_server=sio, socketio_path='socket')

SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"





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
        # print('!!!')
        # print('I want last 10 messages!!!')
        # print('!!!')
        last_messages = await return_last_messages()

        await client_manager.emit('receive_last_messages_from_chat', data=last_messages, room=sid, namespace='/messaging')

# show send message
async def return_saved_message(message):
    await  client_manager.emit('show_saved_message', data={'message': message}, room='chat_room', namespace='/messaging')




server.register_namespace(MessagingNamespace('/messaging'))