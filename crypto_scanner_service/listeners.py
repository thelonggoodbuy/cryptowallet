from fastapi import Depends
from propan.fastapi import RabbitRouter
from propan_config.router import exchange_get_all_transcations,\
                                 queue_get_all_transcations,\
                                 rabbit_router


from crypto_scanner_service.services.eth_crypro_scanner import etherium_crypro_scanner


rabbit_etherium_service_listener_router = RabbitRouter("amqp://guest:guest@localhost:5672")


@rabbit_router.broker.handle(queue_get_all_transcations, exchange_get_all_transcations)
async def get_all_transactions_message(message: dict):

    data = message['data']
    sid = message['sid']
    await etherium_crypro_scanner.return_all_transactions_by_wallet(data, sid)

