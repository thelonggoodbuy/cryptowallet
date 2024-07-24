from jose import jwt
from src.users.repository.user_repository import user_rep_link
import os
# from src.users.dependencies import get_password_hash


# SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
# ALGORITHM = "HS256"
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
ALGORITHM = os.environ.get('JWT_ALGORITHM')


class UserService:
    async def return_email_by_token(token: str) -> str:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email

    async def return_user_per_email(email: str):
        user = await user_rep_link.return_user_per_email(email)
        return user

    async def return_user_data_by_id(user_id):
        user = await user_rep_link.return_user_data_by_id(user_id)
        user_dict = {"username": user.username, "email": user.email}
        if user.photo:
            user_dict["user_photo"] = user.photo["url"][1:]
        else:
            user_dict["user_photo"] = None
        return user_dict

    async def update_user(validated_update_user_or_error):
        match validated_update_user_or_error:
            case dict():
                result = {
                    "status": "unvalidated",
                    "errors": validated_update_user_or_error,
                }

            case UpdateUserModel:  # noqa: F841
                updated_user_data = await user_rep_link.update_user(
                    validated_update_user_or_error
                )
                result = {"status": "updated", "data": updated_user_data}

        return result

    async def registrate_user(user_after_validation):
        print("***")
        print(user_after_validation)
        print("***")
        match user_after_validation.data_status:
            case "validated":
                new_user_fictive_formdata = (
                    await user_rep_link.save_user_and_return_unhashed_password(
                        user_after_validation
                    )
                )

                result = {
                    "status": "validated",
                    "fictive_form_data": new_user_fictive_formdata,
                }
            case "error":
                result = {"status": "error", "errors": user_after_validation.cause}
            case _:
                result = {"status": "error"}
        return result

    async def return_all_users():
        all_users = await user_rep_link.return_all_users()
        return all_users

    @classmethod
    async def check_if_user_is_admin_by_token(cls, access_token: str) -> bool:
        jvt_result_decode = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user = await cls.return_user_per_email(jvt_result_decode['sub'])
        print('=====!!!======')
        print(user.is_admin)
        print('==============')
        if user.is_admin == True:
            return True
        else:
            return False

    @classmethod
    async def check_if_admin_user_exist(cls) -> bool:
        admin_is_exist_status = await user_rep_link.check_if_admin_user_exist()
        if admin_is_exist_status:
            return True
        else:
            return False
