from redis import asyncio as aioredis
import json
import ast
from db_config.database import get_db
from src.users.models import User




redis_url = "redis://localhost/1"
redis_connection = aioredis.from_url(redis_url)


async def add_user_to_chat_redis_hash(sid, email):
    user_data = await redis_connection.hget("users_in_chat", email)
    user_status_dict = {}

    match user_data:
        case None:
            generator = get_db()
            session = next(generator)
            user = session.query(User).filter(User.email==email).first()
            user_data_dict = {'id': user.id,
                    'username': user.username}
            if user.photo:
                user_data_dict['user_photo'] = user.photo['url'][1:]
            else:
                user_data_dict['user_photo'] = None

            user_data_dict = {'user_data': user_data_dict, 'email': email, 'connection_quantity': 1, 'sid_list': [sid, ]}

            await redis_connection.hmset('users_in_chat', mapping={email: str(user_data_dict)})
            user_status_dict['status'] = 'new'
            user_status_dict['user_data'] = user_data_dict
        
        case bytes:
            user_data_dict = ast.literal_eval(user_data.decode('utf-8'))
            user_data_dict['connection_quantity'] += 1
            sid_list = user_data_dict['sid_list']
            match sid_list:
                case None:
                    sid_list = [sid,]
                case list:
                    sid_list.append(sid)
            user_data_dict['sid_list'] = sid_list
            await redis_connection.hmset('users_in_chat', mapping={email: str(user_data_dict)})
            user_status_dict['status'] = 'in_system'

    await redis_connection.close()
    return user_status_dict



async def delete_user_from_chat_redis_hash(sid, email):
    # print("---disconnect data:---")
    # print(sid)
    # print(email)
    # print("----------------------")
    user_data = await redis_connection.hget("users_in_chat", email)
    user_data_dict = ast.literal_eval(user_data.decode('utf-8'))
    user_data_dict['connection_quantity'] -= 1

    # print('------DELETING USER DATA------')
    # print(user_data_dict)
    # print('------------------------------')

    disconnect_user_status = {}

    if user_data_dict['connection_quantity'] <= 0:
        await redis_connection.hdel('users_in_chat', email)
        disconnect_user_status['status'] = 'disconnected'
        disconnect_user_status['id'] = user_data_dict['user_data']['id']
        # await 

    else:
        sid_list = user_data_dict['sid_list']
        sid_list.remove(sid)
        user_data_dict['sid_list'] = sid_list
        await redis_connection.hmset('users_in_chat', mapping={email: str(user_data_dict)})
        disconnect_user_status['status'] = 'connected'
    return disconnect_user_status


async def add_seed_email_pair(sid, email):
    await redis_connection.hmset('seed_email_pairs', mapping={sid: email})



async def return_email_by_seed_and_delete(sid):
    email = await redis_connection.hmget('seed_email_pairs', sid)
    await redis_connection.hdel('seed_email_pairs', sid)

    return email


import json

async def return_all_online_user():
    all_users = await redis_connection.hgetall('users_in_chat')
    #  print('------All----users-----')
    #  print(all_users)
    #  print('-----------------------')
    users_in_chat_now = []
    if bool(all_users):
        for user_key in all_users:
        # dictionary = json.loads(all_users.decode('utf-8'))
            
            dictionary = ast.literal_eval(all_users[user_key].decode('utf-8'))
            # print('***')
            # print(dictionary)
            # print('***')
            users_in_chat_now.append(dictionary['user_data'])
    #  print('-----------------------')
    return users_in_chat_now


