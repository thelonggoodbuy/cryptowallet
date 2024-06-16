# class User(Base):
#     __tablename__ = "user"
#     __table_args__ = (
#         UniqueConstraint("email"),
#     )

#     id: Mapped[int] = mapped_column(primary_key=True)
#     email: Mapped[str] = mapped_column(String(70))
#     password: Mapped[str] = mapped_column(String(70))
#     username: Mapped[str] = mapped_column(String(70))
#     is_active: Mapped[bool] = mapped_column(default=False)
#     # photo: mapped_column(FileField())
#     photo = Column(FileField)


# class Message(Base):
#     __tablename__ = "message"


#     id: Mapped[int] = mapped_column(primary_key=True)
#     text: Mapped[str] = mapped_column(TEXT)
#     # user FK
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     user: Mapped["User"] = relationship(back_populates="messages")


# class Wallet(Base):
#     __tablename__ = "wallet"
#     __table_args__ = (
#         UniqueConstraint("private_key"),
#     )
#     id: Mapped[int] = mapped_column(primary_key=True)
#     private_key: Mapped[str] = mapped_column(String(300))
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     user: Mapped["User"] = relationship(back_populates="wallets")
#     address: Mapped[str] = mapped_column(String(300))
#     # balance: mapped_column(DECIMAL(10, 9))
#     balance = Column(DECIMAL(10, 9))
#     # assey FK
#     asset_id: Mapped[int] = mapped_column(ForeignKey("asset.id"))
#     user: Mapped["Asset"] = relationship(back_populates="wallets")


# class Asset(Base):
#     __tablename__ = "asset"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     type: Mapped[str] = mapped_column(ENUM("currency", "token"))
#     text: Mapped[str] = mapped_column(TEXT)
#     decimal_places: Mapped[int] = mapped_column(Integer())
#     title: Mapped[str] = mapped_column(String(70))
#     # blockchain: FK
#     blockchain_id: Mapped[int] = mapped_column(ForeignKey("blockchain.id"))
#     blockchain: Mapped["Blockchain"] = relationship(back_populates="assets")

#     code: Mapped[str] = mapped_column(String(70))


# class Blockchain(Base):
#     __tablename__ = "blockchain"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     blockchain_type: Mapped[str] = mapped_column(ENUM("eth_like", "bitcoin_like", "unique"))
#     title: Mapped[str] = mapped_column(String(70))
#     # logo: mapped_column(FileField())
#     photo = Column(FileField)


# class Transaction(Base):
#     __tablename__ = "transaction"


#     id: Mapped[int] = mapped_column(primary_key=True)
#     # wallet FK
#     wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"))
#     wallet: Mapped["Wallet"] = relationship(back_populates="transactions")

#     send_to: Mapped[str] = mapped_column(String(70))
#     # value: mapped_column(DECIMAL(10, 9))
#     value = Column(DECIMAL(10, 9))


#     txn_hash: Mapped[str] = mapped_column(String(200))
#     # date_time_transaction: mapped_column(DATETIME())
#     date_time_transaction = DATETIME()
#     txn_hash: Mapped[str] = mapped_column(String(200))
#     status: Mapped[str] = mapped_column(ENUM("success", "fail", "pending"))


# class Commodity(Base):
#     __tablename__ = "commodity"


#     id: Mapped[int] = mapped_column(primary_key=True)
#     # wallet FK
#     wallet_id: Mapped[int] = mapped_column(ForeignKey("wallet.id"))
#     wallet: Mapped["Wallet"] = relationship(back_populates="wallets")

#     title: Mapped[str] = mapped_column(String(70))
#     # price: mapped_column(DECIMAL(10, 9))
#     price = Column(DECIMAL(10, 9))

#     # photo: mapped_column(FileField())
#     photo = Column(FileField())


# class Order(Base):
#     __tablename__ = "order"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     # one to one Commodity
#     commodity_id: Mapped[int] = mapped_column(ForeignKey("commodity.id"))
#     commodity: Mapped["Commodity"] = relationship(back_populates="orders")
#     # one to one Transaction
#     transaction_id: Mapped[int] = mapped_column(ForeignKey("transaction.id"))
#     transaction: Mapped["Transaction"] = relationship(back_populates="orders")

#     # date_time_transaction: mapped_column(DATETIME())
#     date_time_transaction = Column(DATETIME())
#     status: Mapped[str] = mapped_column(ENUM("new", "delivery", "complete", "fail"))
