from pydantic import BaseModel, validator
from typing import Optional


class CommoditySchema(BaseModel):
    title: str
    price: str
    wallet: str
    photo: bytes
    # user: Optional[User] = None

    @validator("title")
    def title_must_not_be_empty(cls, value):
        if not value:
            raise ValueError("Заголовок має бути вказаним.")
        return value

    @validator("price")
    def price_must_be_positive_decimal(cls, value):
        value = value.replace(",", ".")
        try:
            price = float(value)
            if price <= 0:
                raise ValueError("Вартість товару має бути більшу нуля.")
        except ValueError:
            raise ValueError("Ціна має бути вказанною.")
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
    field: str | None = None
    # type: str


class ErrorResponse(BaseModel):
    errors: list[ErrorSchema]


class UpdateOrderSchema(BaseModel):
    """
    schema for updating order data.
    it content user_id for response to
    FrontEnd throw python SocketIO server
    to SocketIO client on FrontEnd

    parameters:
    order_id: int
    status: str
    user_id: int
    """

    order_id: int
    status: str
    user_id: int
    return_transaction_id: Optional[str] = None


class OrderEvent(BaseModel):
    order_dict: dict
