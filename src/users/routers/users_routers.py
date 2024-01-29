from fastapi import Depends, APIRouter, status, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from starlette.responses import RedirectResponse

from datetime import datetime, timedelta, timezone

from typing import Annotated

from jose import JWTError, jwt
from pydantic import BaseModel

from passlib.context import CryptContext



SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 0.1



fake_users_db = {
    "johndoe@example.com": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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




# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user




async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user




async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



# OAuth2PasswordRequestForm

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    # payload: Dict[Any, Any]
) -> Token:

    user = authenticate_user(fake_users_db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")







@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user




@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.username}]




# def fake_decode_token(token):
#     return User(
#         username=token + "fakedecoded", email="john@example.com"
#     )


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     user = fake_decode_token(token)
#     return user




# @router.get("/users/me")
# async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
#     return current_user





# @router.get("/users/items/")
# async def read_items(token: Annotated[str, Depends(get_current_user)]):
#     return 






# --------------------------######----------------------------------
from jose import JWTError, jwt

# class AccessToken(BaseModel):
#     access_token: str

from fastapi import Request

@router.post("/users/validate_access_token/")
async def validate_access_token(request: Request):
    print(request)
    print(await request.json())
    json_data = await request.json()
    token = json_data['access_token']
    # print('==============')
    # print(token)
    # print('==============')
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print('-------------------JVT-DECODE--------------------------------')
    print(token)
    print(payload)
    print('-------------------!!!!--------------------------------')





@router.get("/users/test_response/")
async def test_response(current_user: Annotated[User, Depends(get_current_active_user)]):
    item = {"response": "you are authentoicated!"}
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)



@router.get("/users/login/", response_class=HTMLResponse)
async def login():

    with open('front/login.html', 'r') as file:
        data = file.read()
    
    return HTMLResponse(content=data, status_code=200)




@router.post("/users/send_login_data/")
async def send_login_data():
    print('RECEIVE!')
    item = {"response": "success from server!"}
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)






@router.get("/users/profile/", response_class=HTMLResponse)
async def profile(current_user: Annotated[User, Depends(get_current_active_user)]):
    with open('front/user_profile.html', 'r') as file:
        data = file.read()
    return HTMLResponse(content=data, status_code=200)