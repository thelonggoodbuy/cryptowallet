
from src.users.pydantic_models import MessageFromChatModel
from .models import User, Message
from sqlalchemy.orm import Session
from db_config.database import get_db
from fastapi import Depends
import os
from propan_config.router import add_to_returning_saved_message_query


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

    print('----new message----')
    # print(message)
    # print(message.user.photo)
    # user_photo_url = message.user.photo['url'][1:]
    # print(user_photo_url)
    message_dict = {}
    message_dict = {'message': message.text,
                    'username': user.username}
    if user.photo:
        message_dict['user_phoro'] = user.photo['url'][1:]
    else:
        message_dict['user_phoro'] = None

    if message.photo:
        message_dict['message_phoro'] = message.photo['url'][1:]

    print(message_dict)
    await add_to_returning_saved_message_query(message_dict)
    print('----new message----')
    # add_to_returning_saved_message_query()
    # print(type(message))

