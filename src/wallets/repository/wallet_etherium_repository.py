from abc import ABC, abstractmethod
from src.wallets.repository.wallet_abstract_repository import WalletAbstractRepository

from sqlalchemy.orm import Session
from db_config.database import get_db, get_async_session, engine
from sqlalchemy import select
from src.wallets.models import Wallet, Asset

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload, contains_eager
from sqlalchemy.orm import lazyload




class WalletEtheriumRepository(WalletAbstractRepository):


    async def return_wallets_per_user(self, user):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Wallet).options(contains_eager(Wallet.asset)\
                                    .contains_eager(Asset.blockchain))\
                                    .filter(Wallet.user==user)

            wallets = await session.execute(query)
            result = wallets.scalars()
            await session.commit()
        return result


    async def return_wallet_per_id(self, id):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Wallet).options(contains_eager(Wallet.asset)\
                                    .contains_eager(Asset.blockchain))\
                                    .filter(Wallet.id == int(id)).limit(1)
            result = await session.execute(query)
            wallet = result.scalars().one()
            await session.commit()
        return wallet


    async def update_wallet_ballance(self, wallet_id, new_balance):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Wallet).options(contains_eager(Wallet.asset)\
                                .contains_eager(Asset.blockchain))\
                                .filter(Wallet.id == wallet_id).limit(1)
            
            result = await session.execute(query)
            wallet = result.scalars().one()
            wallet.balance = new_balance
            await session.commit()
        return wallet
    

    async def create_new_wallet(self, private_key, user, address, asset, balance=0):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            wallet = Wallet(private_key=private_key,
                                user=user,
                                address=address,
                                balance=balance,
                                asset=asset
                                )
            session.add(wallet)
            await session.commit()
            query = select(Wallet).options(contains_eager(Wallet.asset)\
                                .contains_eager(Asset.blockchain))\
                                .filter(Wallet.id == wallet.id)
            result = await session.execute(query)
            wallet = result.scalars().first()
            await session.commit()
        return wallet
        


wallet_eth_rep_link = WalletEtheriumRepository()