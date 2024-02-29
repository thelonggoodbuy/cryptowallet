from fastapi import Depends, FastAPI

from src.users.routers import users_routers

# from src.users.models import User, Message
# from src.wallets.models import Wallet, Asset, Blockchain
# from src.etherium.models import Transaction
# from src.orders.models import Commodity, Order

from db_config.database import engine
from db_config import database
# from propan_config.app import rabbit_router


from fastapi.staticfiles import StaticFiles

import asyncio


from src.users.models import User, Message
from src.wallets.models import Wallet, Asset, Blockchain
from src.etherium.models import Transaction
from src.orders.models import Commodity, Order
from socketio_config.server import socket_app
from propan_config.router import rabbit_router
# new!
from contextlib import asynccontextmanager
from src.users.listeners import rabbit_users_listener_router
from socketio_config.listeners import rabbit_sockets_listener_router


database.Base.metadata.create_all(bind=engine)





# lifespan_dict = {}


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Load the ML model
#     # ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
#     lifespan_dict['rabbit_router'] = rabbit_router.lifespan_context
#     yield
#     # Clean up the ML models and release the resources
#     # ml_models.clear()


# app = FastAPI(lifespan=lifespan)


app = FastAPI(lifespan=rabbit_router.lifespan_context)


app.mount("/static", StaticFiles(directory="front", html=True), name="static")
app.mount("/media", StaticFiles(directory="media", html=True), name="media")
app.mount("/socket", app=socket_app)


app.include_router(users_routers.router)
# new!
app.include_router(rabbit_router)
app.include_router(rabbit_users_listener_router)
app.include_router(rabbit_sockets_listener_router)


@app.get("/")
async def root():    
    return {"message": "Cryptowallet main app!"}


