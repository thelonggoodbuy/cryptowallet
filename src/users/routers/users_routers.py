from fastapi import Cookie, Depends, APIRouter, status, HTTPException, Request, Response, Form
from fastapi.responses import HTMLResponse, JSONResponse

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.users.utils import OAuth2PasswordBearerWithCookie

from starlette.responses import RedirectResponse

from datetime import datetime, timedelta, timezone

from typing import Annotated, Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from passlib.context import CryptContext

from jose.exceptions import ExpiredSignatureError



SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 0.25



fake_users_db = {
    "johndoe@example.com": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice@example.com": {
        "username": "alice",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,

    },
}





router = APIRouter()

# ------------------------USER LOGIC FROM DOC--------------------

# -------------->>>>>>>>>>>>>>>models<<<<<<<<<<<<<<<<<<<<<-------


class Token(BaseModel):
    access_token: str
    token_type: str



class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)



def get_user(db, email: str):
    if email in db:
        user_dict = db[email]
        return UserInDB(**user_dict)
    

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
    #     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # else:
    #     expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




async def get_current_user(request:Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print('---------#1----------------')
    try:
        # token in request----
        token = request.cookies['access_token']
        print('---------#2---TOKEN--------')
        print(token)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print('---------#3----------------')
        print(payload)
        username: str = payload.get("sub")
        print(username)
        if username is None:
            
            raise credentials_exception
        token_data = TokenData(username=username)

        user = get_user(fake_users_db, email=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    

    except JWTError:
        print('---------#4----------------')
        redirect_url = '/users/login/'
        # raise credentials_exception
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    except KeyError:
        print('---------#5----------------')
        redirect_url = '/users/login/'
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    



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
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
# ) -> Token:


    user = authenticate_user(fake_users_db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    # remember_me_form_data = filter(lambda x: x.startswith('remember-me'), form_data.scopes)
    remember_me_form_data = [i for i in form_data.scopes if i.startswith('remember_me')]
    remember_me_status = remember_me_form_data[0].replace("remember_me:","")

    if remember_me_status == 'true':
        # print('***REMEMBER***ME****')
        access_token = create_access_token(
            data={"sub": user.email}
        )
    else:
        # print('***FORGET***ME***')
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

    response.set_cookie(key="access_token_in_backend",value=f"Bearer {access_token}", httponly=True)
    return Token(access_token=access_token, token_type="bearer")





# @router.get("/users/test_response/")
# # async def test_response(current_user: Annotated[User, Depends(get_current_active_user)], request: Request):
# async def test_response(request: Request):
#     # print('#1#')
#     # print('---login---cookie---')
#     # print(request.cookies)
#     # print('--------------------')
#     item = {"response": "you are authentoicated!"}
#     return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)



@router.get("/users/login/", response_class=HTMLResponse)
async def login(request: Request):

    with open('front/login.html', 'r') as file:
        data = file.read()
    # print('---login---cookie---')
    # print(request.cookies)
    # print('--------------------')
    return HTMLResponse(content=data, status_code=200)




# @router.post("/users/send_login_data/")
# async def send_login_data():
#     # print('RECEIVE!')
#     item = {"response": "success from server!"}
#     return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)




@router.get("/users/profile/", response_class=HTMLResponse)
async def profile(current_user_or_redirect: Annotated[User, Depends(get_current_user)], 
                  request: Request,
                  response: Response,
                  cookies: Optional[str] = Cookie(None)):
    

    match current_user_or_redirect:
        case UserInDB():
            with open('front/user_profile.html', 'r') as file:
                data = file.read()
            return HTMLResponse(content=data, status_code=200)
        case RedirectResponse():
            return current_user_or_redirect
        




@router.get("/users/registration/", response_class=HTMLResponse)
async def registration(request: Request):

    with open('front/registration.html', 'r') as file:
        data = file.read()
    # print('---login---cookie---')
    # print(request.cookies)
    # print('--------------------')
    return HTMLResponse(content=data, status_code=200)






# -------------------------->>>>>>>>>>Pydantic----validation<<<<<<<<<<<<<<<-----------------------------------

from typing import Union
from typing import List

class NewUserModel(BaseModel):

    email: str
    username: str | None
    password: str
    repeat_password: str
    data_status: str | None
    # cause: str | None
    cause: Optional[List[dict]] = None

    @classmethod
    def as_form(
        cls,
        email: str = Form(),
        # username: str | None = Form(),
        username: str = Form(default=None),
        password: str = Form(),
        repeat_password: str = Form(),
        data_status: str = 'unvalidated',
        cause: str | None = []
    ):

        return cls(email=email, 
                   username=username, 
                   password=password, 
                   repeat_password=repeat_password,
                   data_status=data_status,
                   cause=cause)


from email_validator import validate_email, EmailNotValidError
from password_validator import PasswordValidator
from sqlalchemy.orm import Session
from db_config.database import get_db
from src.users.models import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def validate_new_user(new_user_model: NewUserModel = Depends(NewUserModel.as_form),
                      db: Session = Depends(get_db)):
    print('***now we validate register data!***')

    # 1.1 email validation. correct email
    try:
        # check if email is valid
        emailinfo = validate_email(new_user_model.email, check_deliverability=False)
        normalized_form =  emailinfo.normalized
        new_user_model.email = normalized_form

        db_user = get_user_by_email(db, email=new_user_model.email)
        if db_user:
            new_user_model.cause.append({'email':'Цей емейл вже використовeється іншим користувачем.'})


    except EmailNotValidError:
        # new_user_model.data_status = 'error'
        new_user_model.cause.append({'email':'Емейл було введено з помилкою!'})

    # 1.2 email validation. check if email exist in DB!
    # -------------->>>>><<<<<<<-----------------------
    # -------------->>>>><<<<<<<-----------------------
    # -------------->>>>><<<<<<<-----------------------

    # 2.1 username validation. is username exist
    if new_user_model.username == None:
        # new_user_model.data_status = 'error'
        new_user_model.cause.append({'username':'Необхідно заповнити юзернейм'})


    # 3.1 password validation. check if password is saved
    pasword_schema = PasswordValidator()
    if pasword_schema.min(8).validate(new_user_model.password) == False: new_user_model.cause.append({'password':'Пароль не може бути меньшим, ніж 8 символів'})
    # if pasword_schema.max(20) == False: new_user_model.cause.append({'password':'Пароль не може бути більшим, ніж 20 символів'})
    if pasword_schema.has().symbols().validate(new_user_model.password) == False: new_user_model.cause.append({'password':'Пароль повинен містити хочаб один знак'})
    if pasword_schema.has().lowercase().validate(new_user_model.password) == False: new_user_model.cause.append({'password':'Пароль повинен містити хочаб одну маленьку літеру'})
    if pasword_schema.has().uppercase().validate(new_user_model.password) == False: new_user_model.cause.append({'password':'Пароль повинен містити хочаб одну велику літеру'})
    if pasword_schema.has().digits().validate(new_user_model.password) == False: new_user_model.cause.append({'password':'Пароль повинен містити хочаб одну цифру'})

    
    # 4.1
    # pasword and repeat password check
    if new_user_model.password != new_user_model.repeat_password:
        new_user_model.cause.append({'repeat password':'Данні в полі "пароль" та "повторити пароль" повинні співпадати!'})

    if len(new_user_model.cause) == 0:
        new_user_model.data_status = 'validated'
    else:
        new_user_model.data_status = 'error'

    return new_user_model



@router.post("/users/registration_data/")
async def registration_data(user_after_validation: NewUserModel = Depends(validate_new_user), 
                            db: Session = Depends(get_db)):

    match user_after_validation.data_status:
        case "validated":
            new_user = User(
                email=user_after_validation.email,
                password=get_password_hash(user_after_validation.password),
                username=user_after_validation.username,
                is_active=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            result = {"status": "validated"}
            
        case "error":
            result = {"status": "error", "errors": user_after_validation.cause}
        case _:
            result = {"status": "error"}

    return result

