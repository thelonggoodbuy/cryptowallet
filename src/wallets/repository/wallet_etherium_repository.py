from abc import ABC, abstractmethod
from src.wallets.repository.wallet_abstract_repository import WalletAbstractRepository

from sqlalchemy.orm import Session
from db_config.database import engine
from sqlalchemy import select
from src.wallets.models import Wallet, Asset
from src.users.models import User

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload, contains_eager
from sqlalchemy.orm import lazyload
from sqlalchemy.orm import load_only



class WalletEtheriumRepository(WalletAbstractRepository):
    """
    Asynchronous repository providing methods for 
    interacting with Ethereum wallet objects in the database.
    """


    async def return_wallets_per_user(self, user: User) -> list[Wallet]:
        """
        Retrieves all Ethereum wallet objects from the 
        database owned by a specific user.

        Args:
            user(User): The user object representing the wallet owner.
                        
        Returns:
            result(list[Wallet]) : A list of Ethereum wallet objects owned by the user, 
                or an empty list if the user has no wallets.
        """
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Wallet).options(contains_eager(Wallet.asset)\
                                    .contains_eager(Asset.blockchain))\
                                    .filter(Wallet.user==user)

            wallets = await session.execute(query)
            result = wallets.scalars()
            await session.commit()
        return result


    async def return_wallet_per_id(self, id: int) -> Wallet:
        """
        Retrieves Ethereum wallet by id.

        Args:
            id(int): wallet id.
                        
        Returns:
            result(list[Wallet]) : Ethereum wallet.
        """
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Wallet).options(contains_eager(Wallet.asset)\
                                    .contains_eager(Asset.blockchain))\
                                    .filter(Wallet.id == int(id)).limit(1)
            result = await session.execute(query)
            wallet = result.scalars().one()
            await session.commit()
        return wallet
    

    async def return_wallet_per_address(self, wallet_address):
        print(wallet_address)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Wallet).options(contains_eager(Wallet.asset)\
                                    .contains_eager(Asset.blockchain))\
                                    .options(contains_eager(Wallet.user))\
                                    .where(Wallet.address == wallet_address)
            wallet = await session.execute(query)
            result = wallet.scalars().first()

            await session.commit()

        return result

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
        

    async def return_all_wallets_addresses(self) -> dict:
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Wallet)
            result = await session.execute(query)
            wallets = result.scalars()
            await session.commit()
        addresses_dict = {}
        for wallet in wallets: 
            # print(wallet.address)
            addresses_dict[wallet.address] = wallet.user_id

        return addresses_dict


    async def return_all_wallets_adresses_per_user_id(self, user_id):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Wallet).options(load_only(Wallet.address)).filter(Wallet.user_id==user_id)
            result = await session.execute(query)
            wallets = result.scalars()
            await session.commit()
        addresses_set = set()
        for wallet in wallets: 
            # print(wallet.address)
            addresses_set.add(wallet.address)
        return addresses_set
    

    async def return_user_id_by_wallet_id(self, wallet_id):
        print('Wallet id is')
        print(type(wallet_id))
        print(wallet_id)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Wallet).where(Wallet.id == int(wallet_id))
            wallet = await session.execute(query)
            result = wallet.scalars().first()
            print('result is')
            print(result)
            owner_id = result.user_id
            await session.commit()

        return owner_id


wallet_eth_rep_link = WalletEtheriumRepository()