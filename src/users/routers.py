from fastapi import Depends, APIRouter, status, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from src.users.services.user_service import UserService
from src.users.services.message_service import MessageService
from src.wallets.services.wallet_etherium_service import WalletEtheriumService
import os

from fastapi.security import OAuth2PasswordRequestForm


from starlette.responses import RedirectResponse


from datetime import timedelta

from typing import Annotated

from jose import jwt


from jose.exceptions import ExpiredSignatureError


# from src.users.models import User
from src.users.schemas import Token, User, UserInDB, UpdateUserModel, NewUserModel


from src.users.dependencies import (
    authenticate_user,
    create_access_token,
    get_current_user,
    validate_update_user,
    validate_new_user,
)


# SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
# ALGORITHM = "HS256"
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
ALGORITHM = os.environ.get('JWT_ALGORITHM')

ACCESS_TOKEN_EXPIRE_MINUTES = 0.25


router = APIRouter()


@router.post("/users/validate_access_token/")
async def validate_access_token(request: Request):
    json_data = await request.json()
    token = json_data["access_token"]
    token_from_backend = request.cookies["access_token_in_backend"].replace(
        "Bearer ", ""
    )

    if token_from_backend == token:
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print('***')


            print(decoded_token['sub'])
            user = await UserService.return_user_per_email(decoded_token['sub'])
            print(user)

            print('***')
            if user:
                result = {"result": True}
            else:
                result = {"result": False, "cause": "user doesnt exist"}
        except ExpiredSignatureError:
            result = {"result": False, "cause": "token_expiced"}
    else:
        result = {"result": False, "cause": "token_doesnt_match"}
    return result


@router.post("/token/")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response
):
    print("---login-formdata---")
    print(form_data)
    print("--------------------")
    user = await authenticate_user(form_data.username, form_data.password)
    print("---user---")
    print(user)
    print("----------")
    if not user:
        print('===>NO USER NO USER NO USER NO USER<===')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        

    remember_me_form_data = [i for i in form_data.scopes if i.startswith("remember_me")]
    remember_me_status = remember_me_form_data[0].replace("remember_me:", "")

    if remember_me_status == "true":
        access_token = create_access_token(data={"sub": user.email})
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

    response.set_cookie(
        key="access_token_in_backend", value=f"Bearer {access_token}", httponly=True
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/login/", response_class=HTMLResponse)
async def login(request: Request):
    with open("templates/login.html", "r") as file:
        data = file.read()

    return HTMLResponse(content=data, status_code=200)


@router.get("/users/profile/", response_class=HTMLResponse, name="user_profile")
async def profile(current_user_or_redirect: Annotated[User, Depends(get_current_user)]):
    match current_user_or_redirect:
        case UserInDB():
            with open("templates/user_profile.html", "r") as file:
                data = file.read()
            return HTMLResponse(content=data, status_code=200)

        case RedirectResponse():
            return current_user_or_redirect


@router.post("/users/get_current_user_data/")
async def profile_current_data(
    current_user_or_redirect: Annotated[User, Depends(get_current_user)],
):
    print('===current===user===data====')
    match current_user_or_redirect:
        case UserInDB():
            print('====user in db===')
            # data for updating user form
            user = await UserService.return_user_per_email(
                email=current_user_or_redirect.email
            )
            try:
                photo_url = user.photo["url"][1:]
            except TypeError:
                photo_url = None

            # data about quantity messages
            total_messages_by_user = await MessageService.return_quantity_of_concrete_user(user.id)
            print('===total_messages_by_user===')
            print(total_messages_by_user)

            # total users wallets
            total_wallets_by_user = await WalletEtheriumService.return_wallets_per_user_email_without_sync(current_user_or_redirect.email)
            wallets_quantity = len(total_wallets_by_user)
            print('===wallets_quantity===')
            print(wallets_quantity)
            print('======================')

            data = {
                "username": user.username,
                "email": user.email,
                "photo_url": photo_url,
                "total_messages_by_user": total_messages_by_user,
                "wallets_quantity": wallets_quantity
            }

            return data

        case RedirectResponse():
            return current_user_or_redirect


@router.post("/users/update_profile/")
async def update_profile(
    validated_update_user_or_error: UpdateUserModel | dict = Depends(
        validate_update_user
    ),
):
    return await UserService.update_user(validated_update_user_or_error)


@router.get("/users/registration/", response_class=HTMLResponse)
async def registration(request: Request):
    with open("templates/registration.html", "r") as file:
        data = file.read()
    return HTMLResponse(content=data, status_code=200)


@router.post("/users/registration_data/")
async def registration_data(
    response: Response, user_after_validation: NewUserModel = Depends(validate_new_user)
):
    result = await UserService.registrate_user(user_after_validation)
    if result["status"] == "validated":
        token = await login_for_access_token(result["fictive_form_data"], response)
        result = {"status": "validated", "access_token": token}

    return result


# ------------------------------CHAT--------LOGIC-------------------------------------------
@router.get("/users/chat/", response_class=HTMLResponse)
async def chat(request: Request, current_user_or_redirect: Annotated[User, Depends(get_current_user)]):
    match current_user_or_redirect:
        case UserInDB():
            with open("templates/chat.html", "r") as file:
                data = file.read()
            return HTMLResponse(content=data, status_code=200)
        case RedirectResponse():
            return current_user_or_redirect
        

# @router.get("/users/profile/", response_class=HTMLResponse, name="user_profile")
# async def profile(current_user_or_redirect: Annotated[User, Depends(get_current_user)]):
#     match current_user_or_redirect:
#         case UserInDB():
#             with open("templates/user_profile.html", "r") as file:
#                 data = file.read()
#             return HTMLResponse(content=data, status_code=200)

#         case RedirectResponse():
#             return current_user_or_redirect
