from fastapi import Depends
from propan.fastapi import RabbitRouter

from propan_config.router import exchange_get_all_transcations,\
                                 queue_get_all_transcations,\
                                 rabbit_router

# from etherium_config.services.eth_scanner import ETHScannerService
from crypto_scanner_service.services.eth_crypro_scanner import etherium_crypro_scanner


# from src.users.schemas import MessageFromChatModel
# from src.users.services.message_service import MessageService



rabbit_etherium_service_listener_router = RabbitRouter("amqp://guest:guest@localhost:5672")


@rabbit_router.broker.handle(queue_get_all_transcations, exchange_get_all_transcations)
async def get_all_transactions_message(message: dict):

    # print('***')
    print('LISTENER WORK!')
    print(message)
    data = message['data']
    sid = message['sid']
    print('***')
    await etherium_crypro_scanner.return_all_transactions_by_wallet(data, sid)
    # message = MessageFromChatModel(message=message,

