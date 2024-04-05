from jose import jwt
from src.users.repository.user_repository import user_rep_link

import locale
from src.users.schemas import UpdateUserModel
from src.users.dependencies import get_password_hash


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
    

    async def update_user(validated_update_user_or_error):
        match validated_update_user_or_error:
            case dict():
                result = {"status": "unvalidated", "errors": validated_update_user_or_error}

            case UpdateUserModel:
                updated_user_data = user_rep_link.update_user(validated_update_user_or_error)

                # user_email = validated_update_user_or_error.email
                # # user_object = db.query(models.User).filter(models.User.email == user_email).first()

                # user_object = user_rep_link.return_user_per_email(email=user_email)
                # user_object.username = validated_update_user_or_error.username

                # if validated_update_user_or_error.delete_image == True:
                #     user_object.photo = None
                # elif validated_update_user_or_error.photo:
                #     print('change photo!')
                #     user_object.photo = validated_update_user_or_error.photo
                # if 'password' in UpdateUserModel:
                #     user_object.password = get_password_hash(validated_update_user_or_error.password)

                # db.commit()

                # if user_object.photo != None:
                #     photo_url = user_object.photo['url'][1:]
                # else:
                #     photo_url = None

                # updated_user_data = {
                #     'username': user_object.username,
                #     'email': user_object.email,
                #     'photo_url': photo_url
                # }

                result = {'status': 'updated', 'data': updated_user_data}

        return result


    