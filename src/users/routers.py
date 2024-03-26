from fastapi import Depends, APIRouter, status, HTTPException, Request, Response, Form, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse

from fastapi.security import OAuth2PasswordRequestForm


from starlette.responses import RedirectResponse



from datetime import timedelta

from typing import Annotated

from jose import jwt


from jose.exceptions import ExpiredSignatureError


from sqlalchemy.orm import Session
from db_config.database import get_db
from src.users.models import User
from src.users.schemas import Token, User, UserInDB, UpdateUserModel, NewUserModel, FictiveFormData

from src.users import models

from src.users.dependencies import pwd_context, oauth2_scheme, verify_password, \
                                    get_password_hash, get_user_by_email, get_user,\
                                    authenticate_user, create_access_token, get_current_user,\
                                    validate_update_user, validate_new_user


SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 0.25


router = APIRouter()
 

@router.post("/users/validate_access_token/")
async def validate_access_token(request: Request):

    json_data = await request.json()
    token = json_data['access_token']
    token_from_backend = request.cookies['access_token_in_backend'].replace("Bearer ","")

    if token_from_backend == token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            result = {'result': True}
        except ExpiredSignatureError:
            result = {'result': False, 'cause': 'token_expiced'}
    else:
        result = {'result': False, 'cause': 'token_doesnt_match'}
    return result




@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                response: Response,
                                db: Session = Depends(get_db)):

    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    remember_me_form_data = [i for i in form_data.scopes if i.startswith('remember_me')]
    remember_me_status = remember_me_form_data[0].replace("remember_me:","")

    if remember_me_status == 'true':
        access_token = create_access_token(
            data={"sub": user.email}
        )
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

    response.set_cookie(key="access_token_in_backend",value=f"Bearer {access_token}", httponly=True)
    return Token(access_token=access_token, token_type="bearer")



@router.get("/users/login/", response_class=HTMLResponse)
async def login(request: Request):

    with open('front/login.html', 'r') as file:
        data = file.read()

    return HTMLResponse(content=data, status_code=200)



@router.get("/users/profile/", response_class=HTMLResponse)
async def profile(current_user_or_redirect: Annotated[User, Depends(get_current_user)]):
    
    match current_user_or_redirect:
        case UserInDB():
            with open('front/user_profile.html', 'r') as file:
                data = file.read()
            return HTMLResponse(content=data, status_code=200)
        
        case RedirectResponse():
            return current_user_or_redirect
        



@router.post("/users/get_current_user_data/")
async def profile_current_data(current_user_or_redirect: Annotated[User, Depends(get_current_user)],
                               db: Session = Depends(get_db)):
    
    match current_user_or_redirect:
        case UserInDB():

            user_query = db.query(models.User).filter(models.User.email==current_user_or_redirect.email)
            user = user_query.first()

            try:
                photo_url = user.photo['url'][1:]
            except TypeError:
                photo_url = None

            data = {
                'username': user.username,
                'email': user.email,
                'photo_url': photo_url
            }

            return data
        
        case RedirectResponse():
            return current_user_or_redirect




@router.post("/users/update_profile/")
async def update_profile(validated_update_user_or_error: UpdateUserModel|dict = Depends(validate_update_user),
                         db: Session = Depends(get_db)):
    

    match validated_update_user_or_error:
        case dict():
            result = {"status": "unvalidated", "errors": validated_update_user_or_error}

        case UpdateUserModel:
            user_email = validated_update_user_or_error.email
            user_object = db.query(models.User).filter(models.User.email == user_email).first()
            user_object.username = validated_update_user_or_error.username

            if validated_update_user_or_error.delete_image == True:
                user_object.photo = None
            elif validated_update_user_or_error.photo:
                print('change photo!')
                user_object.photo = validated_update_user_or_error.photo
            if 'password' in UpdateUserModel:
                user_object.password = get_password_hash(validated_update_user_or_error.password)

            db.commit()
            if user_object.photo != None:
                photo_url = user_object.photo['url'][1:]
            else:
                photo_url = None

            updated_user_data = {
                'username': user_object.username,
                'email': user_object.email,
                'photo_url': photo_url
            }

            result = {'status': 'updated', 'data': updated_user_data}
    return result


@router.get("/users/registration/", response_class=HTMLResponse)
async def registration(request: Request):
    with open('front/registration.html', 'r') as file:
        data = file.read()
    return HTMLResponse(content=data, status_code=200)


@router.post("/users/registration_data/")
async def registration_data(response: Response,
                            user_after_validation: NewUserModel = Depends(validate_new_user),
                            db: Session = Depends(get_db)):

    match user_after_validation.data_status:
        case "validated":
            new_user = models.User(
                email=user_after_validation.email,
                password=get_password_hash(user_after_validation.password),
                username=user_after_validation.username,
                is_active=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            fictive_form_data = FictiveFormData(username=user_after_validation.email, 
                                                password=user_after_validation.password, 
                                                scopes=['remember_me:true',])

            token = await login_for_access_token(fictive_form_data, 
                                response,
                                db)

            result = {"status": "validated", "access_token": token}
        case "error":
            result = {"status": "error", "errors": user_after_validation.cause}
        case _:
            result = {"status": "error"}
    return result


# ------------------------------CHAT--------LOGIC-------------------------------------------
@router.get("/users/chat/", response_class=HTMLResponse)
async def chat(request: Request, current_user_or_redirect: Annotated[User, Depends(get_current_user)]):

    match current_user_or_redirect:
        case UserInDB():
            with open('front/chat.html', 'r') as file:
                data = file.read()
            return HTMLResponse(content=data, status_code=200)
        case RedirectResponse():
            return current_user_or_redirect
