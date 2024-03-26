from propan_config.router import queue_return_saved_messages, exchange_return_saved_messages, rabbit_router,\
                                    exchange_return_new_wallet, queue_return_new_wallet,\
                                    exchange_update_wallet_list, queue_update_wallet_list
from propan.fastapi import RabbitRouter
from socketio_config.server import return_saved_message, return_new_wallet, update_wallet_state



rabbit_sockets_listener_router = RabbitRouter("amqp://guest:guest@localhost:5672")

@rabbit_router.broker.handle(queue_return_saved_messages, exchange_return_saved_messages)
async def receive_saved_chat_message(message: dict):
    await return_saved_message(message)


@rabbit_router.broker.handle(queue_return_new_wallet, exchange_return_new_wallet)
async def receive_new_wallet(message: dict):
    print('Receive new wallet!')
    await return_new_wallet(message)


@rabbit_router.broker.handle(queue_update_wallet_list, exchange_update_wallet_list)
async def return_updated_wallets(message: dict):
    print('---you want to update wallet!---')
    print(message)
    print('--------------------------------')
    # await update_wallet_state(message)