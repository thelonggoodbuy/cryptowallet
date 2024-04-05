from fastapi import Form
from typing import List, Optional

from pydantic import BaseModel, computed_field
from pydantic import field_validator, model_validator
from pydantic_core.core_schema import FieldValidationInfo

from password_validator import PasswordValidator
from datetime import datetime





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


class UpdateUserModel(BaseModel):

    email: str
    username: str
    password: str | None = None
    repeat_password: str | None = None
    photo: bytes | None = None
    delete_image: bool = False

    class Config:
        orm_mode = True

    @field_validator('password')
    def validate_password_structure(cls, value: str, values: FieldValidationInfo):
        pasword_schema = PasswordValidator()
        if pasword_schema.min(8).validate(value) == False: 
            raise ValueError('Пароль не може бути меньшим, ніж 8 символів')
        if pasword_schema.has().symbols().validate(value) == False: 
            raise ValueError('Пароль повинен містити хочаб один знак')
        if pasword_schema.has().lowercase().validate(value) == False: 
            raise ValueError('Пароль повинен містити хочаб одну маленьку літеру')
        if pasword_schema.has().uppercase().validate(value) == False:
            raise ValueError('Пароль повинен містити хочаб одну велику літеру')
        if pasword_schema.has().digits().validate(value) == False:
            raise ValueError('Пароль повинен містити хочаб одну цифру')
        return value
    
    @field_validator('repeat_password')
    def validate_repeat_password_match(cls, value: str, values: FieldValidationInfo):
        if "password" in values.data and value != values.data['password']:
            raise ValueError("Паролі не співпадають")

    @model_validator(mode='before')
    def validate_password_and_repeat_password_not_empty(cls, data):

        if ('password' in data and 'repeat_password' not in data) or\
            ('password' not in data and 'repeat_password' in data):
            raise ValueError('Для зміни паролю потрібно ввести пароль, та повторити його. Одне з полів пусте.')
        else:
            return data


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
    

class MessageFromChatModel(BaseModel):
    message: str
    email: str
    photo: bytes | str | None = None


    @model_validator(mode='before')
    def validate_photo(cls, data):
        if 'photo' in data:
            dt = datetime.now()
            ts = datetime.timestamp(dt)
            filename = data['email'] + '__' + str(ts)

            with open(f'media/external_storage/{filename}', 'wb') as f: 
                f.write(data['photo'])

            data['photo'] = filename
        return data
