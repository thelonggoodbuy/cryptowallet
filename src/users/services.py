
from src.users.pydantic_models import MessageFromChatModel
from .models import User, Message
from sqlalchemy.orm import Session
from db_config.database import get_db
from fastapi import Depends
import os


# @rabbit_router.broker.handle(queue_1, exch)
async def save_new_message(message_from_socket: MessageFromChatModel):

    generator = get_db()
    session = next(generator)
    user = session.query(User).filter(User.email==message_from_socket.email).first()
    message = Message(text=message_from_socket.message)
    message.user = user

    if message_from_socket.photo != None:
        with open(f'media/external_storage/{message_from_socket.photo}', 'rb') as photo: 
            message.photo = photo
            session.add(message)
            session.commit()
        os.remove(f'media/external_storage/{message_from_socket.photo}')

    else:
        session.add(message)
        session.commit()

    print(message)
    print(type(message))