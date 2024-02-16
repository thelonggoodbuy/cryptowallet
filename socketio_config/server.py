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

@sio.event
async def connect(sid, environ):
    print(sid, "New Client Connected to This id :"+" "+str(sid))


@sio.event
async def disconnect(sid):
    print(sid, "Client Disconnected: "+" "+str(sid))







# @sio.on('*')
# async def any_event(event, sid, data):
#     print('---Connection work!---')





#Socket io (sio) create a Socket.IO server
# sio=socketio.AsyncServer(cors_allowed_origins='*',async_mode='asgi')















# class ChatNamespace(socketio.AsyncNamespace):
#     def on_connect(self, sid, environ):
#         print('------CHAT!-------')
#         print('Chat connect!')
#         pass

#     def on_disconnect(self, sid):
#         print('------CHAT!-------')
#         print('Chat disconnect!')
#         pass

#     async def send_message(self, sid, data):
#         print('------CHAT!-------')
#         print('Chat send message')
#         # await self.emit('my_response', data)


# sio.register_namespace(ChatNamespace('/chat_socket'))