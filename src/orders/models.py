from sqlalchemy import String, ForeignKey, DECIMAL, DateTime, Column

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy_utils.types.choice import ChoiceType


from sqlalchemy_file import FileField

from src.wallets.models import Wallet
from src.etherium.models import Transaction
# from db_config.models import Base
from db_config.database import Base
from datetime import datetime





# class Base(DeclarativeBase):
#     pass
# from db_config.models import Base


class Commodity(Base):
    __tablename__ = "commodity"


    id: Mapped[int] = mapped_column(primary_key=True)
    # wallet FK
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"))
    wallet: Mapped["Wallet"] = relationship(backref="wallets")

    title: Mapped[str] = mapped_column(String(70))
    # price: mapped_column(DECIMAL(10, 9))
    price = Column(DECIMAL(10, 9))
    
    # photo: mapped_column(FileField())
    photo = Column(FileField())


class Order(Base):
    __tablename__ = "order"
    ORDER_STATUS = (
        ("new", "New"),
        ("delivery", "Delivery"),
        ("complete", "Complete"),
        ("fail", "Fail")
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # one to one Commodity
    commodity_id: Mapped[int] = mapped_column(ForeignKey("commodity.id"))
    commodity: Mapped["Commodity"] = relationship(backref="orders")
    # one to one Transaction
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transaction.id"))
    transaction: Mapped["Transaction"] = relationship(backref="orders")

    # date_time_transaction: mapped_column(DATETIME())
    # date_time_transaction = Column(DATETIME())
    date_time_transaction = Column(DateTime, default=datetime.now)
    # order_status: Mapped[str] = mapped_column(ENUM("new", "delivery", "complete", "fail"))
    # order_status: Mapped[str] = mapped_column(ENUM("new", "delivery", "complete", "fail"))
    order_status = Column(ChoiceType(ORDER_STATUS))



