from fastapi import Depends, FastAPI

from src.users.routers import users_routers

# from src.users.models import User, Message
# from src.wallets.models import Wallet, Asset, Blockchain
# from src.etherium.models import Transaction
# from src.orders.models import Commodity, Order

from db_config.database import engine
from db_config import database

from fastapi.staticfiles import StaticFiles



from src.users.models import User, Message
from src.wallets.models import Wallet, Asset, Blockchain
from src.etherium.models import Transaction
from src.orders.models import Commodity, Order

# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# Base.metadata.create_all(database.engine)


database.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.mount("/static", StaticFiles(directory="front", html=True), name="static")


app.include_router(users_routers.router)


@app.get("/")
async def root():
    
    return {"message": "Cryptowallet main app!"}