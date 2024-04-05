from redis_config.redis_config import redis_connection
from src.users.services.user_service import UserService
import ast




class RedisUserService():

    # def __init__()
    def __init__(self) -> None:
        self.redis_connection = redis_connection


    async def add_user_to_chat_redis_hash(self, sid, email):
        user_data = await self.redis_connection.hget("users_in_chat", email)
        user_status_dict = {}

        match user_data:
            case None:
                user = await UserService.return_user_per_email(email=email)
                user_data_dict = {'id': user.id,
                        'username': user.username}
                if user.photo:
                    user_data_dict['user_photo'] = user.photo['url'][1:]
                else:
                    user_data_dict['user_photo'] = None

                user_data_dict = {'user_data': user_data_dict, 'email': email, 'connection_quantity': 1, 'sid_list': [sid, ]}

                await self.redis_connection.hmset('users_in_chat', mapping={email: str(user_data_dict)})
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
                await self.redis_connection.hmset('users_in_chat', mapping={email: str(user_data_dict)})
                user_status_dict['status'] = 'in_system'

        await self.redis_connection.close()
        return user_status_dict
    

    async def delete_user_from_chat_redis_hash(self, sid, email):

        user_data = await self.redis_connection.hget("users_in_chat", email)
        user_data_dict = ast.literal_eval(user_data.decode('utf-8'))
        user_data_dict['connection_quantity'] -= 1

        disconnect_user_status = {}

        if user_data_dict['connection_quantity'] <= 0:
            await self.redis_connection.hdel('users_in_chat', email)
            disconnect_user_status['status'] = 'disconnected'
            disconnect_user_status['id'] = user_data_dict['user_data']['id']
        else:
            sid_list = user_data_dict['sid_list']
            sid_list.remove(sid)
            user_data_dict['sid_list'] = sid_list
            await self.redis_connection.hmset('users_in_chat', mapping={email: str(user_data_dict)})
            disconnect_user_status['status'] = 'connected'
        
        await self.redis_connection.close()
        return disconnect_user_status
    

    async def add_seed_email_pair(self, sid, email):
        await self.redis_connection.hmset('seed_email_pairs', mapping={sid: email})
        await self.redis_connection.close()


    async def return_email_by_seed_and_delete(self, sid):
        email = await redis_connection.hmget('seed_email_pairs', sid)
        await redis_connection.hdel('seed_email_pairs', sid)
        await self.redis_connection.close()
        return email
    
    
    async def return_all_online_user(self):
        all_users = await redis_connection.hgetall('users_in_chat')
        users_in_chat_now = []
        if bool(all_users):
            for user_key in all_users:
                dictionary = ast.literal_eval(all_users[user_key].decode('utf-8'))
                users_in_chat_now.append(dictionary['user_data'])
        await self.redis_connection.close()
        return users_in_chat_now
    


redis_user_service = RedisUserService()