from jose import jwt
from src.users.repository.user_repository import user_rep_link

import locale
from src.users.schemas import UpdateUserModel, FictiveFormData
# from src.users.dependencies import get_password_hash


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
                updated_user_data = await user_rep_link.update_user(validated_update_user_or_error)
                result = {'status': 'updated', 'data': updated_user_data}

        return result
    

    async def registrate_user(user_after_validation):
        print('***')
        print(user_after_validation)
        print('***')
        match user_after_validation.data_status:
            case "validated":
                new_user_fictive_formdata = await user_rep_link.save_user_and_return_unhashed_password(user_after_validation)
                # new_user = models.User(
                #     email=user_after_validation.email,
                #     # password=get_password_hash(user_after_validation.password),
                #     username=user_after_validation.username,
                #     is_active=True
                # )
                # db.add(new_user)
                # db.commit()
                # db.refresh(new_user)

                # fictive_form_data = FictiveFormData(username=new_user.email, 
                #                                     password=new_user.password, 
                #                                     scopes=['remember_me:true',])

                # token = await login_for_access_token(fictive_form_data, 
                #                     response,
                #                     db)


                result = {"status": "validated", "fictive_form_data": new_user_fictive_formdata}
            case "error":
                result = {"status": "error", "errors": user_after_validation.cause}
            case _:
                result = {"status": "error"}
        return result


    