from pydantic import BaseModel, ValidationError, validator
from pydantic import model_validator
from typing import Optional
from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from src.orders.services.commodity_eth_service import CommodityEthService
from asgiref.sync import async_to_sync
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError






class OrderRequestSchema(BaseModel):
    accomodation_id: int|str
    wallet_id: int|str


    @validator('accomodation_id')
    def accomodation_id_must_be_integer(cls, value):
        value = int(value)
        return value


    @validator('wallet_id')
    def Wallet_id_must_be_integer(cls, value):
        value = int(value)
        return value


class OrderRequestAsyncValidator:
    @staticmethod
    async def validate_order_data(data):
        wallet = await WalletEtheriumService.return_wallet_per_id(id=data['wallet_id'])
        wallet_balance = wallet.balance

        accomodation = await CommodityEthService.return_commodity_by_id(commodity_id=data['accomodation_id'])
        accomodation_price = accomodation.price

        if wallet_balance < accomodation_price:
            raise ValueError('Недостатньо коштів в гаманці для покупки товару')
        return data
    