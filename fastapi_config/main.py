# import environment
from fastapi_config import environment
import os

from fastapi import FastAPI
from src.users import routers as users_routers
from src.wallets import routers as wallet_routers
from src.orders import routers as orders_routers
from fastapi.staticfiles import StaticFiles
from socketio_config.server import socket_app
from propan_config.router import rabbit_router
from src.users.listeners import rabbit_users_listener_router
from socketio_config.listeners import rabbit_sockets_listener_router
from crypto_scanner_service.listeners import rabbit_etherium_service_listener_router
from delivery_config.listeners import rabbit_etherium_delivery_router
from celery_config.tasks import parse_latest_block_query
from sqladmin import Admin
from db_config.database import engine
from fastapi_config.admin import UserAdmin, MessageAdmin, WalletAdmin, OrderAdmin, CommodityAdmin, TransactionAdmin
from fastapi_config.admin import authentication_backend



app = FastAPI(lifespan=rabbit_router.lifespan_context)

custom_template_path = os.path.join(os.path.dirname(__file__), '../front/sqladmin_custom_templates')

admin = Admin(app,
              engine,
              authentication_backend=authentication_backend,
              templates_dir=custom_template_path)

app.mount("/static", StaticFiles(directory="front", html=True), name="static")
app.mount("/media", StaticFiles(directory="media", html=True), name="media")
app.mount("/socket", app=socket_app)

app.include_router(users_routers.router)
app.include_router(wallet_routers.router)
app.include_router(orders_routers.router)

app.include_router(rabbit_router)
app.include_router(rabbit_users_listener_router)
app.include_router(rabbit_sockets_listener_router)
app.include_router(rabbit_etherium_service_listener_router)
app.include_router(rabbit_etherium_delivery_router)

parse_latest_block_query.delay()

@app.get("/health")
async def health_check():
    return {"status": "OK"}

# admin mounts
admin.add_view(UserAdmin)
admin.add_view(MessageAdmin)
admin.add_view(WalletAdmin)
admin.add_view(OrderAdmin)
admin.add_view(CommodityAdmin)
admin.add_view(TransactionAdmin)
