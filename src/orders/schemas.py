from pydantic import BaseModel, ValidationError, validator
from typing import Optional



class CommoditySchema(BaseModel):
    title: str
    price: str
    wallet: str
    photo: bytes
    # user: Optional[User] = None

    @validator('title')
    def title_must_not_be_empty(cls, value):
        if not value:
            raise ValueError('Заголовок має бути вказаним.')
        return value

    @validator('price')
    def price_must_be_positive_decimal(cls, value):
        value = value.replace(',', '.')
        try:
            price = float(value)
            if price <= 0:
                raise ValueError('Вартість товару має бути більшу нуля.')
        except ValueError:
            raise ValueError('Ціна має бути вказанною.')
        return value

    # @validator('wallet')
    # def wallet_must_be_owned_by_user(cls, value, values):
    #     user = values.get('user')
    #     if user and value not in user.wallets:
    #         raise ValueError('Wallet must be owned by the user')
    #     return value

class ErrorSchema(BaseModel):
    # loc: str
    msg: str
    # type: str

class ErrorResponse(BaseModel):
    errors: list[ErrorSchema]