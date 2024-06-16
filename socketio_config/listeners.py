from propan_config.router import (
    queue_return_saved_messages,
    exchange_return_saved_messages,
    rabbit_router,
    exchange_return_new_wallet,
    queue_return_new_wallet,
    exchange_update_wallet_list,
    queue_update_wallet_list,
    exchange_return_to_socketio_all_transcations,
    queue_return_to_socketio_all_transcations,
    exchange_return_transaction_message_to_socket,
    queue_return_transaction_message_to_socket,
)
from propan.fastapi import RabbitRouter
from socketio_config.server import (
    return_saved_message,
    return_new_wallet,
    return_all_transactions_per_wallet,
)


rabbit_sockets_listener_router = RabbitRouter("amqp://guest:guest@localhost:5672")


@rabbit_router.broker.handle(
    queue_return_saved_messages, exchange_return_saved_messages
)
async def receive_saved_chat_message(message: dict):
    print("---listner save message---")
    await return_saved_message(message)


@rabbit_router.broker.handle(queue_return_new_wallet, exchange_return_new_wallet)
async def receive_new_wallet(message: dict):
    print("Receive new wallet!")
    await return_new_wallet(message)


@rabbit_router.broker.handle(queue_update_wallet_list, exchange_update_wallet_list)
async def return_updated_wallets(message: dict):
    print("---you want to update wallet!---")
    print(message)
    print("--------------------------------")


@rabbit_router.broker.handle(
    queue_return_to_socketio_all_transcations,
    exchange_return_to_socketio_all_transcations,
)
async def return_to_socketio_all_transcations(message: dict):
    # print('--->>>you want to return all data about this wallet TRANSACTIONS <<<---')
    # print(message)
    transaction_data_dict = {
        "scaning_status": message["scaning_status"],
        "wallet_id": message["wallet_id"],
    }
    sid = message["sid"]
    await return_all_transactions_per_wallet(transaction_data_dict, sid)
    # print('--------------------------------')


@rabbit_router.broker.handle(
    queue_return_transaction_message_to_socket,
    exchange_return_transaction_message_to_socket,
)
async def return_transaction_message(message):
    print(
        "------You----want----to----send---data----about---transaction---to---socket------"
    )
    print(message)
    print(
        "---------------------------------------------------------------------------------"
    )
