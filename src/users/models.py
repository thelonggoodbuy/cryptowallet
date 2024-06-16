from sqlalchemy import String, TEXT, ForeignKey
from sqlalchemy import UniqueConstraint, Column, DateTime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy_file import FileField
from db_config.database import Base
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = "user"
    __table_args__ = (UniqueConstraint("email"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(70))
    password: Mapped[str] = mapped_column(String(70))
    username: Mapped[str] = mapped_column(String(70))
    is_active: Mapped[bool] = mapped_column(default=False)
    photo = Column(FileField)
    # !
    messages: Mapped[List["Message"]] = relationship(back_populates="user")


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(TEXT)
    photo = Column(FileField)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    # user FK
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="messages")
