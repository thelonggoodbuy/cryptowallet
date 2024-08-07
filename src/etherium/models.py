from sqlalchemy import String, DECIMAL, DateTime, Column

from sqlalchemy.orm import Mapped, mapped_column


# from db_config.database import Base
from sqlalchemy_utils.types.choice import ChoiceType
from datetime import datetime
from db_config.database import Base


class Transaction(Base):
    __tablename__ = "transaction"
    STATUS = (("success", "Success"), ("fail", "Fail"), ("pending", "Pending"))

    id: Mapped[int] = mapped_column(primary_key=True)
    send_from: Mapped[str] = mapped_column(String(100))
    send_to: Mapped[str] = mapped_column(String(100))
    value = Column(DECIMAL(22, 18))
    txn_hash: Mapped[str] = mapped_column(String(200))
    date_time_transaction = Column(DateTime, default=datetime.now)
    txn_fee = Column(DECIMAL(22, 18))
    status = Column(ChoiceType(STATUS))

    def __str__(self):
        return self.txn_hash
