from sqlalchemy import String, ForeignKey, DECIMAL, DATETIME, Column

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import ENUM

from sqlalchemy_file import FileField

from src.wallets.models import Wallet
from src.etherium.models import Transaction
# from db_config.models import Base
from db_config.database import Base




# class Base(DeclarativeBase):
#     pass
# from db_config.models import Base


class Commodity(Base):
    __tablename__ = "commodity"


    id: Mapped[int] = mapped_column(primary_key=True)
    # wallet FK
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"))
    wallet: Mapped["Wallet"] = relationship(back_populates="wallets")

    title: Mapped[str] = mapped_column(String(70))
    # price: mapped_column(DECIMAL(10, 9))
    price = Column(DECIMAL(10, 9))
    
    # photo: mapped_column(FileField())
    photo = Column(FileField())


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    # one to one Commodity
    commodity_id: Mapped[int] = mapped_column(ForeignKey("commodity.id"))
    commodity: Mapped["Commodity"] = relationship(back_populates="orders")
    # one to one Transaction
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transaction.id"))
    transaction: Mapped["Transaction"] = relationship(back_populates="orders")

    # date_time_transaction: mapped_column(DATETIME())
    date_time_transaction = Column(DATETIME())
    status: Mapped[str] = mapped_column(ENUM("new", "delivery", "complete", "fail"))


