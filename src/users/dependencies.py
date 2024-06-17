from fastapi import Depends, status, HTTPException, Request
from starlette.responses import RedirectResponse

from passlib.context import CryptContext
from email_validator import validate_email, EmailNotValidError
from password_validator import PasswordValidator
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from pydantic import ValidationError

from src.users.schemas import UserInDB, TokenData, UpdateUserModel, NewUserModel
from src.users.utils import OAuth2PasswordBearerWithCookie

from src.users.services.user_service import UserService


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")

SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 0.25


def verify_password(plain_password, hashed_password):
    print("---plain_password---")
    print(plain_password)
    print("---hashed_password---")
    print(hashed_password)
    print("+++++++++++++++++++++")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# !
# async def get_user_by_email(db: Session, email: str):
#     user = await UserService.return_user_per_email(email)
#     return user
# return db.query(user_models.User).filter(user_models.User.email==email).first()


# !
async def get_user(email: str):
    # user = get_user_by_email(db, email)
    user = await UserService.return_user_per_email(email)
    if user:
        user_dict = {
            "hashed_password": user.password,
            "email": user.email,
            "id": user.id,
        }
        return UserInDB(**user_dict)


async def authenticate_user(username: str, password: str):
    print("===auth===user===")
    print(username)
    print(password)
    print("=================")
    user = await get_user(username)
    print("====user====")
    print(user)
    print("============")

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        print("---PASSWORD-IS-NOT-VALIDATED---")
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = request.cookies["access_token"]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

        user = await get_user(email=token_data.username)
        if user is None:
            raise credentials_exception
        return user

    except JWTError:
        print("---END----EXCEPT--1----")
        redirect_url = "/users/login/"
        return RedirectResponse(
            url=redirect_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    except KeyError:
        print("---END----EXCEPT--2----")
        redirect_url = "/users/login/"
        return RedirectResponse(
            url=redirect_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )


async def validate_update_user(request: Request):
    async with request.form() as form:
        update_fields_dict = {}
        for field in form:
            match field:
                case "photo" if form["photo"].size != 0:
                    reared_image = await form["photo"].read()
                    update_fields_dict["photo"] = reared_image
                case "photo" if form["photo"].size == 0:
                    pass
                case _:
                    if form[field] != "":
                        update_fields_dict[field] = form[field]
                    else:
                        pass
    try:
        updated_user = UpdateUserModel(**update_fields_dict)
        result = updated_user
    except ValidationError as exc:
        error_dict = {}
        for error in exc.errors():
            if len(error["loc"]) == 0:
                error_dict["Помилка в формі"] = error["msg"].replace(
                    "Value error, ", ""
                )
            elif error["type"] == "missing":
                error_dict[error["loc"][0]] = "Це поле є обов'язковим для заповнення!"
            elif error["type"] == "value_error":
                error_dict[error["loc"][0]] = error["msg"].replace("Value error, ", "")
        result = error_dict
    return result


# !
async def validate_new_user(
    new_user_model: NewUserModel = Depends(NewUserModel.as_form),
):
    try:
        emailinfo = validate_email(new_user_model.email, check_deliverability=False)
        normalized_form = emailinfo.normalized
        new_user_model.email = normalized_form
        # db_user = get_user_by_email(db, email=new_user_model.email)
        db_user = await UserService.return_user_per_email(email=new_user_model.email)
        if db_user:
            new_user_model.cause.append(
                {"email": "Цей емейл вже використовeється іншим користувачем."}
            )
    except EmailNotValidError:
        new_user_model.cause.append({"email": "Емейл було введено з помилкою!"})
    if not new_user_model.username:
        new_user_model.cause.append({"username": "Необхідно заповнити юзернейм"})

    pasword_schema = PasswordValidator()
    if not pasword_schema.min(8).validate(new_user_model.password):
        new_user_model.cause.append(
            {"password": "Пароль не може бути меньшим, ніж 8 символів"}
        )
    if not pasword_schema.has().symbols().validate(new_user_model.password):
        new_user_model.cause.append(
            {"password": "Пароль повинен містити хочаб один знак"}
        )
    if not pasword_schema.has().lowercase().validate(new_user_model.password):
        new_user_model.cause.append(
            {"password": "Пароль повинен містити хочаб одну маленьку літеру"}
        )
    if not pasword_schema.has().uppercase().validate(new_user_model.password):
        new_user_model.cause.append(
            {"password": "Пароль повинен містити хочаб одну велику літеру"}
        )
    if not pasword_schema.has().digits().validate(new_user_model.password):
        new_user_model.cause.append(
            {"password": "Пароль повинен містити хочаб одну цифру"}
        )
    if new_user_model.password != new_user_model.repeat_password:
        new_user_model.cause.append(
            {
                "repeat password": 'Данні в полі "пароль" та "повторити пароль" повинні співпадати!'
            }
        )
    if len(new_user_model.cause) == 0:
        new_user_model.data_status = "validated"
    else:
        new_user_model.data_status = "error"
    return new_user_model
