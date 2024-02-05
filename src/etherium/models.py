from sqlalchemy import String, ForeignKey, DECIMAL, DateTime, Column

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import ENUM

from src.wallets.models import Wallet
from db_config.database import Base
from sqlalchemy_utils.types.choice import ChoiceType
from datetime import datetime


# from db_config.models import Base

# class Base(DeclarativeBase):
#     pass


class Transaction(Base):
    __tablename__ = "transaction"
    STATUS = (
        ("success", "Success"),
        ("fail", "Fail"),
        ("pending", "Pending")
    )



    id: Mapped[int] = mapped_column(primary_key=True)
    # wallet FK
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"))
    wallet: Mapped["Wallet"] = relationship(backref="transactions")

    send_to: Mapped[str] = mapped_column(String(70))
    # value: mapped_column(DECIMAL(10, 9))
    value = Column(DECIMAL(10, 9))



    txn_hash: Mapped[str] = mapped_column(String(200))

    # date_time_transaction: mapped_column(DATETIME())
    date_time_transaction = Column(DateTime, default=datetime.now)
    
    txn_hash: Mapped[str] = mapped_column(String(200))
    # status: Mapped[str] = mapped_column(ENUM("success", "fail", "pending"))
    status = Column(ChoiceType(STATUS))


