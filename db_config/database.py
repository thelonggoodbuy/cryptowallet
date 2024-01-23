from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from .models import Base

# from src.users.models import User, Message
# from src.wallets.models import Wallet, Asset, Blockchain
# from src.etherium.models import Transaction
# from src.orders.models import Commodity, Order



SQLALCHEMY_DATABASE_URL = "postgresql://maxim:12345qwert@localhost:5432/cryptowallet_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
