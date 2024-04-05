from sqlalchemy.orm import Session
from db_config.database import get_db, get_async_session, engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from src.users.models import User
from src.users.schemas import UpdateUserModel
from src.users.dependencies import get_password_hash




class UserRepository():

    def __init__(self) -> None:
        self.db: Session = get_async_session()


    async def return_user_per_email(self, email):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(User).filter(User.email==email)
            user = await session.execute(query)
            result = user.scalars().first()
            await session.commit()
        return result


    async def return_user_data_by_id(self, user_id):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(User).filter(User.id==int(user_id))
            user = await session.execute(query)
            result = user.scalars().first()
            await session.commit()
        return result


    async def update_user(self, update_data: UpdateUserModel):
        user_email = updated_user_data.email
        # user_object = db.query(models.User).filter(models.User.email == user_email).first()

        # user_object = self.return_user_per_email(email=user_email)

        # user_object.username = validated_update_user_or_error.username

        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            # user_object = self.return_user_per_email(email=user_email)

            query = select(User).filter(User.email==user_email)
            user_object = await session.execute(query)

            user_object.username = update_data.username

            if update_data.delete_image == True:
                user_object.photo = None
            elif update_data.photo:
                print('change photo!')
                user_object.photo = update_data.photo
            if 'password' in UpdateUserModel:
                user_object.password = get_password_hash(update_data.password)

            await session.commit()

            if user_object.photo != None:
                photo_url = user_object.photo['url'][1:]
            else:
                photo_url = None

            updated_user_data = {
                'username': user_object.username,
                'email': user_object.email,
                'photo_url': photo_url
            }

        return updated_user_data
        


user_rep_link = UserRepository()