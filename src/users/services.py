from sqlalchemy import select
from db_config.database import get_db
import os

from src.users.schemas import MessageFromChatModel
from src.users.models import User, Message
from propan_config.router import add_to_returning_saved_message_query
import locale


locale.setlocale(locale.LC_TIME, "uk_UA")


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

    message_dict = {}
    message_dict = {'id': message.id,
                    'message': message.text,
                    'username': user.username,
                    'date_time': message.time_created.strftime('%d %b %H:%M')}
    if user.photo:
        message_dict['user_photo'] = user.photo['url'][1:]
    else:
        message_dict['user_photo'] = None
    if message.photo:
        message_dict['message_photo'] = message.photo['url'][1:]
    await add_to_returning_saved_message_query(message_dict)


async def return_last_messages():
    generator = get_db()
    session = next(generator)
    query = select(Message).join(User).order_by(Message.id.desc()).limit(10).order_by(Message.id.asc())
    messages = session.execute(query).scalars()
    messages_dict = {}
    for message in messages:
        messages_dict[message.id] = {}
        messages_dict[message.id]['id'] = message.id
        messages_dict[message.id]['message'] = message.text
        messages_dict[message.id]['username'] = message.user.username
        messages_dict[message.id]['date_time'] = message.time_created.strftime('%d %b %H:%M')
        if message.user.photo != None:
            messages_dict[message.id]['user_photo'] = message.user.photo['url'][1:]
        else:
            messages_dict[message.id]['user_photo'] = None
        if message.photo != None:
            messages_dict[message.id]['message_photo'] = message.photo['url'][1:]
        else:
            messages_dict[message.id]['message_photo'] = None
    return messages_dict


async def return_user_data_by_id(user_id):
    generator = get_db()
    session = next(generator)
    query = select(User).filter(User.id==user_id)
    user = session.execute(query).scalars().first()
    user_dict = {'username': user.username,
                 'email': user.email,
                 }
    if user.photo != None:
        user_dict['user_photo'] = user.photo['url'][1:]
    else:
        user_dict['user_photo'] = None
    return user_dict
