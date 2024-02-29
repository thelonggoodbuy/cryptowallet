from propan_config.router import queue_return_saved_messages, exchange_return_saved_messages, rabbit_router
from propan.fastapi import RabbitRouter
from socketio_config.server import return_saved_message



rabbit_sockets_listener_router = RabbitRouter("amqp://guest:guest@localhost:5672")

@rabbit_router.broker.handle(queue_return_saved_messages, exchange_return_saved_messages)
async def receive_saved_chat_message(message: dict):

    print('----you---send---message---for----saving---chat---message----')
    print(message)
    await return_saved_message(message)
    print('-------------------------------------------------------------')
