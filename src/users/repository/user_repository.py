from sqlalchemy.orm import Session
from db_config.database import get_async_session, engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext


from src.users.models import User
from src.users.schemas import UpdateUserModel, FictiveFormData
# from src.users.dependencies import get_password_hash
# from src.users.schemas import FictiveFormData


class UserRepository:
    def __init__(self) -> None:
        self.db: Session = get_async_session()

    def get_password_hash(self, password):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    async def return_user_per_email(self, email):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(User).filter(User.email == email)
            user = await session.execute(query)
            result = user.scalars().first()
            await session.commit()
        return result

    async def return_user_data_by_id(self, user_id):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(User).filter(User.id == int(user_id))
            user = await session.execute(query)
            result = user.scalars().first()
            await session.commit()
        return result

    async def update_user(self, update_data: UpdateUserModel):
        user_email = update_data.email
        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            query = select(User).filter(User.email == user_email)
            user_object = await session.execute(query)
            user = user_object.scalars().first()
            user.username = update_data.username

            if update_data.delete_image:
                user.photo = None
            elif update_data.photo:
                print("change photo!")
                user.photo = update_data.photo
            if "password" in update_data:
                user.password = self.get_password_hash(update_data.password)

            await session.commit()

            if not user.photo:
                photo_url = user.photo["url"][1:]
            else:
                photo_url = None

            updated_user_data = {
                "username": user.username,
                "email": user.email,
                "photo_url": photo_url,
            }

        return updated_user_data

    async def save_user_and_return_unhashed_password(self, user_after_validation):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            new_user = User(
                email=user_after_validation.email,
                password=self.get_password_hash(user_after_validation.password),
                username=user_after_validation.username,
                is_active=True,
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

        fictive_form_data = FictiveFormData(
            username=user_after_validation.email,
            password=user_after_validation.password,
            scopes=[
                "remember_me:true",
            ],
        )

        # return {'fictive_form_data': fictive_form_data}

        # token = await login_for_access_token(fictive_form_data,
        #                     response,
        #                     db)
        # return token
        return fictive_form_data


    async def return_all_users(self):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(User)
            result = await session.execute(query)
            users = result.scalars()
            await session.commit()
            return users


    async def check_if_admin_user_exist(self):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(User).filter(User.is_admin == True)
            user = await session.execute(query)
            result = user.scalars().first()
            await session.commit()
        return result

user_rep_link = UserRepository()
