from sqlalchemy.ext.asyncio import async_sessionmaker
from db_config.database import engine
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.users.models import Message
import os


class MessageRepository:
    async def return_last_10_messages_from_chate(self):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = (
                select(Message)
                .options(selectinload(Message.user))
                .order_by(Message.id.desc())
                .limit(10)
                .order_by(Message.id.asc())
            )

            wallets = await session.execute(query)
            result = wallets.scalars()
            await session.commit()
        return result

    async def create_message(self, message_from_socket, user):
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            message = Message(text=message_from_socket.message)
            message.user = user
            if message_from_socket.photo != None:
                with open(
                    f"media/external_storage/{message_from_socket.photo}", "rb"
                ) as photo:
                    message.photo = photo
                    session.add(message)
                    await session.commit()
                os.remove(f"media/external_storage/{message_from_socket.photo}")
            else:
                session.add(message)
                await session.commit()
        return message


message_rep_link = MessageRepository()
