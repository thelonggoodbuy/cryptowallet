# from fastapi import Depends, FastAPI
from pydantic import BaseModel
from propan.fastapi import RabbitRouter
from propan.brokers.rabbit import RabbitExchange, RabbitQueue
# from fastapi_config.main import app
from fastapi import Depends

# propan_config/broker.py

rabbit_router = RabbitRouter("amqp://guest:guest@localhost:5672")
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


exchange_return_saved_messages = RabbitExchange("return_saved_messages_exchange", auto_delete=True)
queue_return_saved_messages = RabbitQueue("return_saved_message", auto_delete=True)

exchange_return_new_wallet = RabbitExchange("return_new_wallet_exchange", auto_delete=True)
queue_return_new_wallet = RabbitQueue("return_new_wallet_query", auto_delete=True)

exchange_update_wallet_list = RabbitExchange("return_update_wallet_list", auto_delete=True)
queue_update_wallet_list = RabbitQueue("update_wallet_list_query", auto_delete=True)


async def add_to_message_query(message):
    await rabbit_router.broker.publish(message, queue="chat_message_query", exchange=exch)
    

async def add_to_returning_saved_message_query(message):
    print('===adding to query new message===')
    await rabbit_router.broker.publish(message, queue="return_saved_message", exchange=exchange_return_saved_messages)


async def return_new_wallet(message):
    await rabbit_router.broker.publish(message, queue="return_new_wallet_query", exchange=exchange_return_new_wallet)


async def add_update_wallet_list_query(message):
    print('---publishing----update----wallet---')
    await rabbit_router.broker.publish(message, queue="update_wallet_list_query", exchange=exchange_update_wallet_list)

# def add_update_wallet_list_query(message):
#     print('---publishing----update----wallet---')
#     rabbit_router.broker.publish(message, queue="update_wallet_list_query", exchange=exchange_update_wallet_list)