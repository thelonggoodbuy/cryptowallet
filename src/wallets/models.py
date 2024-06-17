from sqlalchemy import String, TEXT, ForeignKey, DECIMAL, Integer, Index
from sqlalchemy import UniqueConstraint, Column

from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy_file import FileField
from sqlalchemy_utils.types.choice import ChoiceType
from src.users.models import User
from db_config.database import Base


class Wallet(Base):
    __tablename__ = "wallet"

    __table_args__ = (
        UniqueConstraint("private_key"),
        Index("ix_wallet_user_id", "user_id"),
        Index("ix_wallet_address", "address"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    private_key: Mapped[str] = mapped_column(String(300))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(backref="wallets")
    address: Mapped[str] = mapped_column(String(300))
    balance = Column(DECIMAL(22, 18))
    asset_id: Mapped[int] = mapped_column(ForeignKey("asset.id"))
    asset: Mapped["Asset"] = relationship(backref="wallets")


class Asset(Base):
    __tablename__ = "asset"
    TYPES = (("currency", "Currency"), ("token", "Token"))

    id: Mapped[int] = mapped_column(primary_key=True)
    type = Column(ChoiceType(TYPES))
    text: Mapped[str] = mapped_column(TEXT)
    decimal_places: Mapped[int] = mapped_column(Integer())
    title: Mapped[str] = mapped_column(String(70))
    blockchain_id: Mapped[int] = mapped_column(ForeignKey("blockchain.id"))
    blockchain: Mapped["Blockchain"] = relationship(backref="assets")

    code: Mapped[str] = mapped_column(String(70))


class Blockchain(Base):
    __tablename__ = "blockchain"
    BLOCKCHAINTYPE = (
        ("eth_like", "Etherium_like"),
        ("bitcoin_like", "Bitcoin_like"),
        ("unique", "Unique"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    blockchain_type = Column(ChoiceType(BLOCKCHAINTYPE))
    title: Mapped[str] = mapped_column(String(70))
    photo = Column(FileField)
