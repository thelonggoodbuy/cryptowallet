
from sqlalchemy import String, Boolean, TEXT, ForeignKey, DECIMAL, Integer
from sqlalchemy import UniqueConstraint

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import ENUM

from sqlalchemy_file import FileField

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(70))
    password: Mapped[str] = mapped_column(String(70))
    username: Mapped[str] = mapped_column(String(70))
    is_active: Mapped[bool] = mapped_column(Boolean(default=False))
    photo: mapped_column(FileField())


class Message(Base):
    __tablename__ = "message"


    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(TEXT)
    # user FK
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="messages")


class Wallet(Base):
    __tablename__ = "wallet"
    __table_args__ = (
        UniqueConstraint("private_key"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    private_key: Mapped[str] = mapped_column(String(300))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="wallets")
    address: Mapped[str] = mapped_column(String(300))
    balance: mapped_column(DECIMAL(10, 9))
    # assey FK
    asset_id: Mapped[int] = mapped_column(ForeignKey("asset.id"))
    user: Mapped["Asset"] = relationship(back_populates="wallets")


class Asset(Base):
    __tablename__ = "asset"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(ENUM("currency", "token"))
    text: Mapped[str] = mapped_column(TEXT)
    decimal_places: Mapped[int] = mapped_column(Integer())
    title: Mapped[str] = mapped_column(String(70))
    # blockchain: FK
    blockchain_id: Mapped[int] = mapped_column(ForeignKey("blockchain.id"))
    blockchain: Mapped["Blockchain"] = relationship(back_populates="blockchain")

    code: Mapped[str] = mapped_column(String(70))


class Blockchain(Base):
    __tablename__ = "blockchain"

    id: Mapped[int] = mapped_column(primary_key=True)
    blockchain_type: Mapped[str] = mapped_column(ENUM("eth_like", "bitcoin_like", "unique"))
    title: Mapped[str] = mapped_column(String(70))
    logo: mapped_column(FileField())