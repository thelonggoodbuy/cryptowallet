# from fastapi import Depends, FastAPI
from pydantic import BaseModel
from propan.fastapi import RabbitRouter
from propan.brokers.rabbit import RabbitExchange, RabbitQueue
import os
# from fastapi_config.main import app

# propan_config/broker.py

RABBIT_ADDRESS = os.environ.get('RABBIT_ADDRESS')


rabbit_router = RabbitRouter(RABBIT_ADDRESS)
# app = FastAPI(lifespan=router.lifespan_context)

exch = RabbitExchange("exchange", auto_delete=True)
queue_1 = RabbitQueue("chat_message_query", auto_delete=True)


# socketio_config/server.py otside class


class Incoming(BaseModel):
    m: dict


def call():
    return True


exch = RabbitExchange("exchange", auto_delete=True)
queue_1 = RabbitQueue("chat_message_query", auto_delete=True)


exchange_return_saved_messages = RabbitExchange(
    "return_saved_messages_exchange", auto_delete=True
)
queue_return_saved_messages = RabbitQueue("return_saved_message", auto_delete=True)

exchange_return_new_wallet = RabbitExchange(
    "return_new_wallet_exchange", auto_delete=True
)
queue_return_new_wallet = RabbitQueue("return_new_wallet_query", auto_delete=True)

exchange_update_wallet_list = RabbitExchange(
    "return_update_wallet_list", auto_delete=True
)
queue_update_wallet_list = RabbitQueue("update_wallet_list_query", auto_delete=True)

exchange_get_all_transcations = RabbitExchange(
    "get_all_transcations_exchange", auto_delete=True
)
queue_get_all_transcations = RabbitQueue("get_all_transcations_queue", auto_delete=True)

exchange_return_to_socketio_all_transcations = RabbitExchange(
    "return_to_socketio_all_transcations_exchange", auto_delete=True
)
queue_return_to_socketio_all_transcations = RabbitQueue(
    "return_to_socketio_all_transcations_queue", auto_delete=True
)

exchange_return_transaction_message_to_socket = RabbitExchange(
    "return_transaction_message_to_socket_exchange", auto_delete=True
)
queue_return_transaction_message_to_socket = RabbitQueue(
    "return_transaction_message_to_socket_queue", auto_delete=True
)

exchange_return_data_about_order_to_order_servive = RabbitExchange(
    "return_data_about_order_to_order_servive_exchange", auto_delete=True
)
queue_return_data_about_order_to_order_servive = RabbitQueue(
    "return_data_about_order_to_order_servive_queue", auto_delete=True
)


async def add_to_message_query(message):
    await rabbit_router.broker.publish(
        message, queue="chat_message_query", exchange=exch
    )


async def add_to_returning_saved_message_query(message):
    await rabbit_router.broker.publish(
        message, queue="return_saved_message", exchange=exchange_return_saved_messages
    )


async def return_new_wallet(message):
    await rabbit_router.broker.publish(
        message, queue="return_new_wallet_query", exchange=exchange_return_new_wallet
    )


async def add_update_wallet_list_query(message):
    await rabbit_router.broker.publish(
        message, queue="update_wallet_list_query", exchange=exchange_update_wallet_list
    )


async def add_to_get_all_transcations_queue(message):
    # TODO переписать на нормальный меседжинг
    await rabbit_router.broker.publish(
        message,
        queue="get_all_transcations_queue",
        exchange=exchange_get_all_transcations,
    )


async def add_to_return_to_socketio_all_transcations_queue(message):
    await rabbit_router.broker.publish(
        message,
        queue="return_to_socketio_all_transcations_queue",
        exchange=exchange_return_to_socketio_all_transcations,
    )


async def add_to_return_transaction_message_to_socket(message):
    await rabbit_router.broker.publish(
        message,
        queue="return_transaction_message_to_socket_queue",
        exchange=exchange_return_transaction_message_to_socket,
    )


async def add_to_queue_return_data_about_order_to_order_servive(message):
    await rabbit_router.broker.publish(
        message,
        queue="return_data_about_order_to_order_servive_queue",
        exchange=exchange_return_data_about_order_to_order_servive,
    )
