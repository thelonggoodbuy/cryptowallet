from sqlalchemy import String, ForeignKey, DECIMAL, DATETIME

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import ENUM

from sqlalchemy_file import FileField

from src.microservices.api_gateway_service.models import Wallet
from src.microservices.etherium_service.models import Transaction



class Base(DeclarativeBase):
    pass


class Commodity(Base):
    __tablename__ = "commodity"


    id: Mapped[int] = mapped_column(primary_key=True)
    # wallet FK
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"))
    wallet: Mapped["Wallet"] = relationship(back_populates="wallets")

    title: Mapped[str] = mapped_column(String(70))
    price: mapped_column(DECIMAL(10, 9))
    photo: mapped_column(FileField())


class Order(Base):
    # one to one Commodity
    commodity_id: Mapped[int] = mapped_column(ForeignKey("commodity.id"))
    commodity: Mapped["Commodity"] = relationship(back_populates="commodities")
    # one to one Transaction
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transaction.id"))
    transaction: Mapped["Transaction"] = relationship(back_populates="commodities")

    date_time_transaction: mapped_column(DATETIME())
    status: Mapped[str] = mapped_column(ENUM("new", "delivery", "complete", "fail"))


