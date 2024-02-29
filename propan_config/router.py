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



async def add_to_message_query(message):
    await rabbit_router.broker.publish(message, queue="chat_message_query", exchange=exch)
    

async def add_to_returning_saved_message_query(message):
    await rabbit_router.broker.publish(message, queue="return_saved_message", exchange=exchange_return_saved_messages)



# @rabbit_router.broker.handle(queue_return_saved_messages, exchange_return_saved_messages)
# async def receive_saved_chat_message(message: dict):

#     print('----you---send---message---for----saving---chat---message----')
#     print(message)
#     print('-------------------------------------------------------------')
