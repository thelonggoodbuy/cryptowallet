from db_config.database import engine
from sqlalchemy import select
from src.wallets.models import Wallet, Asset
from src.users.models import User

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import load_only
from src.wallets.models import Blockchain

from src.wallets.schemas import NewBlochainSchema




class BlockchainRepository():


    async def create_blockchain(self, block_chain_data: NewBlochainSchema):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:

            blockchain = Blockchain(blockchain_type=block_chain_data.blockchain_type,
                                    title=block_chain_data.title,
                                    photo=block_chain_data.photo)
            session.add(blockchain)
            # await session.execute(blockchain)
            # result = blockchain_obj.scalars()
            await session.commit()
            query = select(Blockchain).filter(Blockchain.title == block_chain_data.title)
            result = await session.execute(query)
            blockchain_obj = result.scalars().first()
            await session.commit()
        return blockchain_obj



blockchain_rep_link = BlockchainRepository()
