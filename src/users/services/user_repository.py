from sqlalchemy.orm import Session
from db_config.database import get_db, get_async_session, engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from src.users.models import User



class UserRepository():

    def __init__(self) -> None:
        self.db: Session = get_async_session()


    async def return_user_per_email(self, email):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            # query = select(Wallet).options(contains_eager(Wallet.asset)\
            #                         .contains_eager(Asset.blockchain))\
            #                         .filter(Wallet.user==user)
            query = select(User).filter(User.email==email)

            user = await session.execute(query)
            result = user.scalars().first()
            await session.commit()
        return result



user_rep_link = UserRepository()