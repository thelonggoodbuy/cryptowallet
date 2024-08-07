from propan.fastapi import RabbitRouter
from propan_config.router import (
    rabbit_router,
    exchange_return_data_about_order_to_order_servive,
    queue_return_data_about_order_to_order_servive,
)
import os

# from crypto_scanner_service.services.eth_crypro_scanner import etherium_crypro_scanner
RABBIT_ADDRESS = os.environ.get('RABBIT_ADDRESS')


rabbit_etherium_delivery_router = RabbitRouter(RABBIT_ADDRESS)


@rabbit_router.broker.handle(
    queue_return_data_about_order_to_order_servive,
    exchange_return_data_about_order_to_order_servive,
)
async def get_order_data_from_parser(message: dict):
    print(
        "*************************************ORDER DATA FROM PARSER*************************************"
    )
    print(message)
    print(
        "================================================================================================="
    )
