from fastapi import Depends, FastAPI

from src.users import routers as users_routers
from src.wallets import routers as wallet_routers
from src.orders import routers as orders_routers
from db_config.database import engine, Base
from db_config import database


from fastapi.staticfiles import StaticFiles


from asyncio import create_task
import asyncio


from src.users.models import User, Message
from src.wallets.models import Wallet, Asset, Blockchain
from src.etherium.models import Transaction
from src.orders.models import Commodity, Order
from socketio_config.server import socket_app, client_manager
from propan_config.router import rabbit_router
# new!
from contextlib import asynccontextmanager
from src.users.listeners import rabbit_users_listener_router
from socketio_config.listeners import rabbit_sockets_listener_router
from crypto_scanner_service.listeners import rabbit_etherium_service_listener_router
from delivery_config.listeners import rabbit_etherium_delivery_router

# from crypto_parser_service.services.etherium_parser_service import run_etherium_parser

from asyncio import create_task
from celery_config.tasks import parse_latest_block_query, handle_block
from celery import chain

from crypto_parser_service.services.etherium_parser_service import ETHParserService


app = FastAPI(lifespan=rabbit_router.lifespan_context)


app.mount("/static", StaticFiles(directory="front", html=True), name="static")
app.mount("/media", StaticFiles(directory="media", html=True), name="media")
app.mount("/socket", app=socket_app)


app.include_router(users_routers.router)
app.include_router(wallet_routers.router)
app.include_router(orders_routers.router)


# new!
app.include_router(rabbit_router)
app.include_router(rabbit_users_listener_router)
app.include_router(rabbit_sockets_listener_router)
app.include_router(rabbit_etherium_service_listener_router)
app.include_router(rabbit_etherium_delivery_router)


parse_latest_block_query.delay()

# parse_latest_block_query.apply_async((), handle_block.s())
# parse_latest_block_query.link(handle_block.s())
# parse_latest_block_query.delay()
# chain(parse_latest_block_query.s(), handle_block.s()).apply_async()



@app.get("/health")
async def health_check():
    return {"status": "OK"}
