from fastapi import Cookie, Depends, APIRouter, status, HTTPException, Request, Response, Form, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.users.utils import OAuth2PasswordBearerWithCookie

from starlette.responses import RedirectResponse

from typing import Union

from datetime import datetime, timedelta, timezone

from typing import Annotated, Optional

from jose import JWTError, jwt
from pydantic import BaseModel, ConfigDict

from passlib.context import CryptContext

from jose.exceptions import ExpiredSignatureError


from email_validator import validate_email, EmailNotValidError
from password_validator import PasswordValidator
from sqlalchemy.orm import Session
from db_config.database import get_db
from src.users.models import User



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
    username: str | None = None
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



def get_user(db: Session, email: str):
    user = get_user_by_email(db, email)

    if user:
        user_dict = {"hashed_password": user.password, "email": user.email}
        return UserInDB(**user_dict)
    
    

def authenticate_user(db: Session, username: str, password: str):

    user = get_user(db, username)
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

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




async def get_current_user(request:Request,
                           db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = request.cookies['access_token']
        # print('get---current---user---')

        # print(token)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print(payload)

        username: str = payload.get("sub")
        # print(username)

        if username is None:    
            raise credentials_exception
        token_data = TokenData(username=username)

        user = get_user(db, email=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    

    except JWTError:
        print('---END----EXCEPT--1----')
        redirect_url = '/users/login/'
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    except KeyError:
        print('---END----EXCEPT--2----')
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
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                                response: Response,
                                db: Session = Depends(get_db)):

    print('---------1-----------')
    print(form_data)
    print('--------------------')

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
        



from sqlalchemy_file import File
from sqlalchemy_file.storage import StorageManager

@router.post("/users/get_current_user_data/")
async def profile_current_data(current_user_or_redirect: Annotated[User, Depends(get_current_user)],
                               db: Session = Depends(get_db)):
    
    match current_user_or_redirect:
        case UserInDB():

            user_query = db.query(models.User).filter(models.User.email==current_user_or_redirect.email)
            user = user_query.first()

            print(user.photo['url'])

            data = {
                'username': user.username,
                'email': user.email,
                'photo_url': user.photo['url'][1:]
            }
            print(data)
            
            return data
        
        case RedirectResponse():
            return current_user_or_redirect


from typing import List

class UpdateUserModel(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    username: str | None
    password: str | None
    repeat_password: str | None
    # photo: File | None
    photo: Union[File, UploadFile, str, None]
    data_status: str | None
    cause: Optional[List[dict]] = None

    @classmethod
    def as_form(
        cls,
        username: str = Form(default=None),
        password: str = Form(default=None),
        repeat_password: str = Form(default=None),
        photo: str = Form(default=None),
        data_status: str = 'unvalidated',
        cause: List | None = []
    ):

        return cls(username=username, 
                   password=password, 
                   repeat_password=repeat_password,
                   photo=photo,
                   data_status=data_status,
                   cause=cause)



from io import StringIO
from starlette.datastructures import FormData

@router.post("/users/update_profile/")
# async def update_profile(current_user_or_redirect: Annotated[User, Depends(get_current_user)],
#                         update_user_model: UpdateUserModel = Depends(UpdateUserModel.as_form),
#                         db: Session = Depends(get_db)):
# async def update_profile(username: Annotated[str, Form()],
#                          password: Annotated[str, Form()],
#                          repeat_password: Annotated[str, Form()],
#                          photo: Annotated[str, Form()]):

# async def update_profile(username: Annotated[str, Form()] = None,
#                          password: Annotated[str, Form()] = None,
#                          repeat_password: Annotated[str, Form()] = None,
#                          photo:  UploadFile | None = None):

# async def update_profile(username: Annotated[str, Form()], photo: Annotated[str, Form()]):

# async def update_profile(username: Annotated[str, Form()], photo: UploadFile):

# async def update_profile(photo: UploadFile):
async def update_profile(request: Request, db: Session = Depends(get_db)):
    

    async with request.form() as form:

        email = form["email"]

        update_fields_dict = {}
        user_object = db.query(models.User).filter(models.User.email == email).first()

        print('---Iterations----')
        for field in form:
            match field:
                case 'photo' if form['photo'].size != 0:
                    reared_image = await form['photo'].read()
                    update_fields_dict['photo'] = reared_image
                case 'photo' if form['photo'].size == 0:
                    pass
                case 'email':
                    pass
                case _:
                    if form[field] != '':
                        update_fields_dict[field] = form[field]
                    else:
                        pass

        # print(update_fields_dict)

        for field in update_fields_dict: setattr(user_object, field, update_fields_dict[field])

        db.commit()

        print('*')

    return {'photo': 'All right'}








@router.get("/users/registration/", response_class=HTMLResponse)
async def registration(request: Request):

    with open('front/registration.html', 'r') as file:
        data = file.read()
    # print('---login---cookie---')
    # print(request.cookies)
    # print('--------------------')
    return HTMLResponse(content=data, status_code=200)






# -------------------------->>>>>>>>>>Pydantic----validation<<<<<<<<<<<<<<<-----------------------------------



class NewUserModel(BaseModel):

    email: str
    username: str | None
    password: str
    repeat_password: str
    data_status: str | None
    cause: Optional[List[dict]] = None

    @classmethod
    def as_form(
        cls,
        email: str = Form(),
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



from src.users import models


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email==email).first()



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





class FictiveFormData(BaseModel):
    username: str
    password: str
    scopes: list[str]

    @property
    def username(self):
        return self.username
    
    @property
    def username(self):
        return self.password
    
    @property
    def scopes(self):
        return self.scopes




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
            # ----------------->>>

            fictive_form_data = FictiveFormData(username=user_after_validation.email, 
                                                password=user_after_validation.password, 
                                                scopes=['remember_me:true',])

            token = await login_for_access_token(fictive_form_data, 
                                response,
                                db)
            print('token in registration data!')
            print(token)
            # response.set_cookie(key="access_token_in_backend",value=f"Bearer {token}", httponly=True)


            # ----------------->>>
            result = {"status": "validated", "access_token": token}



            
        case "error":
            result = {"status": "error", "errors": user_after_validation.cause}
        case _:
            result = {"status": "error"}

    return result

