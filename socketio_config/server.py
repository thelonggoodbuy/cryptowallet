import socketio

# SOCKETIO_MOUNTPOINT = "/bar"  # MUST START WITH A FORWARD SLASH
SOCKETIO_PATH = "socket"
# While some tutorials use "*" as the cors_allowed_origins value, this is not safe practice.
CLIENT_URLS = ["http://localhost:8000", "ws://localhost:8000"]



# sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(socketio_server=sio, socketio_path='socket')



# sio = socketio.Server(cors_allowed_origins=[
#     'http://localhost:8000',
#     'https://admin.socket.io',
# ])

# sio = socketio.Server(cors_allowed_origins=['*'], async_mode='asgi')




# @sio.event
# async def connect(sid, environ):
#     print(sid, "New Client Connected to This id :"+" "+str(sid))



# @sio.on('connect', namespace='/messaging')
# async def connect(sid, environ):
#     print('----')
#     print(sid, "New Client Connected to This id :"+" "+str(sid))
#     print('----')




# @sio.on('disconnect', namespace='/messaging')
# async def disconnect(sid):
#     print('----')
#     print(sid, "Client Disconnected: "+" "+str(sid))
#     print('----')

from jose import JWTError, jwt
from redis_config.redis_config import add_user_to_chat_redis_hash,\
                                    add_seed_email_pair,\
                                    return_email_by_seed_and_delete,\
                                    delete_user_from_chat_redis_hash


SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"
import ast

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
        print('------Connect-CHAT!-------')
        print(email)
        print(sid)
        print('--------------------------')


    async def on_disconnect(self, sid):
        # 1. удаление сведений о юзере в селери
        # 2. возвращение сведений в чат

        raw_email_list = await return_email_by_seed_and_delete(sid)
        email = raw_email_list[0].decode()
        print('------DISCONECTD-CHAT!-------')
        print(type(email))
        # email = ast.literal_eval(raw_email.decode('utf-8'))
        
        print(email)
        print(sid)
        await delete_user_from_chat_redis_hash(sid, email)
        print(email)
        print(sid)
        print('-----------------------------')

        pass

    async def send_message(self, sid, data):
        # !!!
        print('------CHAT!-------')
        print('Chat send message')
        # await self.emit('my_response', data)


sio.register_namespace(MessagingNamespace('/messaging'))








# @sio.on('*')
# async def any_event(event, sid, data):
#     print('---Connection work!---')





#Socket io (sio) create a Socket.IO server
# sio=socketio.AsyncServer(cors_allowed_origins='*',async_mode='asgi')














