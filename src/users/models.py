
from sqlalchemy import String, Boolean, TEXT, ForeignKey, DECIMAL, Integer
from sqlalchemy import UniqueConstraint, Column

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import ENUM

from sqlalchemy_file import FileField

# from db_config.models import Base

# class Base(DeclarativeBase):
#     pass

# from db_config.database import Base

from db_config.database import Base

# from db_config.models import Base


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(70))
    password: Mapped[str] = mapped_column(String(70))
    username: Mapped[str] = mapped_column(String(70))
    is_active: Mapped[bool] = mapped_column(default=False)
    # photo: mapped_column(FileField())
    photo = Column(FileField)

    # biography: Mapped[str] = mapped_column(TEXT)


class Message(Base):
    __tablename__ = "message"


    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(TEXT)
    # user FK
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="messages")
