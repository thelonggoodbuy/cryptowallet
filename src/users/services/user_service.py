from jose import jwt
from src.users.repository.user_repository import user_rep_link

import locale



SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"


class UserService():

    
    async def return_email_by_token(token: str) -> str:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    

    async def return_user_per_email(email: str):
        user = await user_rep_link.return_user_per_email(email)
        return user
    

    async def return_user_data_by_id(user_id):
        user = await user_rep_link.return_user_data_by_id(user_id)
        user_dict = {'username': user.username,
                    'email': user.email}
        if user.photo != None:
            user_dict['user_photo'] = user.photo['url'][1:]
        else:
            user_dict['user_photo'] = None
        return user_dict


    