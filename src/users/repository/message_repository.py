from sqlalchemy.ext.asyncio import async_sessionmaker
from db_config.database import engine
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import selectinload

from src.users.models import Message, User
import os



class MessageRepository():


    async def return_last_10_messages_from_chate(self):

        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            query = select(Message).options(selectinload(Message.user))\
                                .order_by(Message.id.desc())\
                                .limit(10)\
                                .order_by(Message.id.asc())

            wallets = await session.execute(query)
            result = wallets.scalars()
            await session.commit()
        return result
    

    async def create_message(self, message_from_socket, user):
        print('===creating message repository===')
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            print('---1---')
            message = Message(text=message_from_socket.message)
            print('---2---')
            message.user = user
            print('---3---')
            if message_from_socket.photo != None:
                print('---4.1---')
                with open(f'media/external_storage/{message_from_socket.photo}', 'rb') as photo: 
                    message.photo = photo
                    session.add(message)
                    # await session.refresh(message)
                    await session.commit()
                os.remove(f'media/external_storage/{message_from_socket.photo}')
            else:
                print('---4.2---')
                session.add(message)
                # await session.refresh(message)
                print('---5.2---')
                await session.commit()
                print('---6.2---')
        return message


message_rep_link = MessageRepository()