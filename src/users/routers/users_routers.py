from fastapi import Cookie, Depends, APIRouter, status, HTTPException, Request, Response
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
ACCESS_TOKEN_EXPIRE_MINUTES = 15



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

# def fake_hash_password(password: str):
#     return "fakehashed" + password


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
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




async def get_current_user(request:Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # token in request----
        token = request.cookies['access_token']

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

        user = get_user(fake_users_db, email=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    

    except JWTError:
        raise credentials_exception
    
    except KeyError:
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

    # token_from_backend = request.cookies
    # print('--------SAVED---TOKEN-----')
    # token_from_backend['access_token_in_backend']
    # print('-------------------------')


    # return result

    



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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )


    response.set_cookie(key="access_token_in_backend",value=f"Bearer {access_token}", httponly=True)
    return Token(access_token=access_token, token_type="bearer")





@router.get("/users/test_response/")
# async def test_response(current_user: Annotated[User, Depends(get_current_active_user)], request: Request):
async def test_response(request: Request):
    # print('#1#')
    print('---login---cookie---')
    print(request.cookies)
    print('--------------------')
    item = {"response": "you are authentoicated!"}
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)



@router.get("/users/login/", response_class=HTMLResponse)
async def login(request: Request):

    with open('front/login.html', 'r') as file:
        data = file.read()
    print('---login---cookie---')
    print(request.cookies)
    print('--------------------')
    return HTMLResponse(content=data, status_code=200)




@router.post("/users/send_login_data/")
async def send_login_data():
    print('RECEIVE!')
    item = {"response": "success from server!"}
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)






@router.get("/users/profile/", response_class=HTMLResponse)
async def profile(current_user_or_redirect: Annotated[User, Depends(get_current_user)], 
                  request: Request,
                  response: Response,
                  cookies: Optional[str] = Cookie(None)):
    
    # async def profile(request: Request):
    # print('----profile----cookies---from---Frontend----------------')
    # print(request.cookies)
    # print('-----dependency result----------------')
    # print(current_user_or_redirect)
    # print(type(current_user_or_redirect))

    match current_user_or_redirect:
        case UserInDB():
            with open('front/user_profile.html', 'r') as file:
                data = file.read()
            return HTMLResponse(content=data, status_code=200)
        case RedirectResponse():
            return current_user_or_redirect