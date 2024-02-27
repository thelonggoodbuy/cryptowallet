from redis import asyncio as aioredis
import json
import ast

redis_url = "redis://localhost/1"
redis_connection = aioredis.from_url(redis_url)


async def add_user_to_chat_redis_hash(sid, email):
    user_data = await redis_connection.hget("users_in_chat", email)

    match user_data:
        case None:
            user_data_dict = {'email': email, 'connection_quantity': 1, 'sid_list': [sid, ]}
            await redis_connection.hmset('users_in_chat', mapping={email: str(user_data_dict)})
        
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

    await redis_connection.close()



async def delete_user_from_chat_redis_hash(sid, email):
    # print("---disconnect data:---")
    # print(sid)
    # print(email)
    # print("----------------------")
    user_data = await redis_connection.hget("users_in_chat", email)
    user_data_dict = ast.literal_eval(user_data.decode('utf-8'))
    user_data_dict['connection_quantity'] -= 1

    if user_data_dict['connection_quantity'] <= 0:
        await redis_connection.hdel('users_in_chat', email)
    else:
        sid_list = user_data_dict['sid_list']
        sid_list.remove(sid)
        user_data_dict['sid_list'] = sid_list
        await redis_connection.hmset('users_in_chat', mapping={email: str(user_data_dict)})



async def add_seed_email_pair(sid, email):
    await redis_connection.hmset('seed_email_pairs', mapping={sid: email})



async def return_email_by_seed_and_delete(sid):
    email = await redis_connection.hmget('seed_email_pairs', sid)
    await redis_connection.hdel('seed_email_pairs', sid)

    return email