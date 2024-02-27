import socketio

SOCKETIO_PATH = "socket"
# While some tutorials use "*" as the cors_allowed_origins value, this is not safe practice.
CLIENT_URLS = ["http://localhost:8000", "ws://localhost:8000"]

import asyncio


sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(socketio_server=sio, socketio_path='socket')


from jose import JWTError, jwt
from redis_config.redis_config import add_user_to_chat_redis_hash,\
                                    add_seed_email_pair,\
                                    return_email_by_seed_and_delete,\
                                    delete_user_from_chat_redis_hash


SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"
import ast



# propan and rabbitmq imports-----------------------------------------------------------------
from propan import PropanApp, RabbitBroker
# from propan_config.router import broker, app
from propan.annotations import Logger
from propan.brokers.rabbit import RabbitExchange, RabbitQueue
# propan and rabbitmq imports-----------------------------------------------------------------

# new!
# from propan_config.router import add_to_message_query, queue_1, exch, Incoming, call
from propan_config.router import add_to_message_query, queue_1, exch, Incoming, call, rabbit_router
from fastapi import Depends

# from fastapi_config.main import add_to_message_query
# from socketio_config.server import app


# exch = RabbitExchange("exchange", auto_delete=True)
# queue_1 = RabbitQueue("chat_message_query", auto_delete=True)

from src.users.pydantic_models import MessageFromChatModel
from datetime import datetime



class MessagingNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        # 1. проверка в селери тут ли находиться этот пользователь
        # 2. сохраненния данных о пользователе в REDIS
        # 3. добавление пользователя в комнату

        token = auth['token']
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        await add_user_to_chat_redis_hash(sid, email)
        await add_seed_email_pair(sid, email)


    async def on_disconnect(self, sid):
        # 1. удаление сведений о юзере в селери
        # 2. возвращение сведений в чат

        raw_email_list = await return_email_by_seed_and_delete(sid)
        email = raw_email_list[0].decode()
        await delete_user_from_chat_redis_hash(sid, email)


    async def on_send_message(self, sid, data):
        # !!!

        print('---socketio---receiver---')
        
        # str(byte_string, encoding='utf-8')
        # data_obj = MessageFromChatModel(message=data['message'], photo=str(data['photo'], encoding='utf-16'))
        
        # photo=data['photo']

        token = data['token']
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        data_obj = MessageFromChatModel(message=data['message'], email=email)

        # print('----user---data---')
        # print(data)
        # print('------------------')

        if 'photo' in data:
            print('data photo exist!!!')
            dt = datetime.now()
            ts = datetime.timestamp(dt)
            filename = email + '__' + str(ts)

            with open(f'media/external_storage/{filename}', 'wb') as f: 
                f.write(data['photo'])

            data_obj.photo = filename

        print('----------')
        print(data_obj)
        print('----------')
        # bytes_value = data['photo']
        # json_values = bytes_value.decode('utf8').replace("'", '"')

        # print(self)
        # print(sid)
        # print(data_obj)
        # print('----')
        await add_to_message_query(data_obj)




sio.register_namespace(MessagingNamespace('/messaging'))


