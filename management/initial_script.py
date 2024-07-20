import sys
import os



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.wallets.schemas import NewBlochainSchema, NewAssetSchema
from src.users.services.user_service import UserService
from src.users.schemas import NewUserModel
from src.wallets.services.blochain_service import BlockchainService
from src.wallets.services.asset_service import AssetService

import asyncio



print('==================INITIAL====SCRIPT======START===============')

async def initialisation():
    print('==================INITIALISATION==ADMIN===USER===============')
    initial_admin_user = await UserService.check_if_admin_user_exist()
    if initial_admin_user:
        print('========ONE==AMIN===USER===WAS===REGISTERED==IN==DB========')
    else:
        admin_data = NewUserModel(
            email = "glison@example.com",
            username = "Glison",
            password = "qL12!kR--5t",
            repeat_password="qL12!kR--5t",
            data_status = "validated",
            is_admin=True
        )
        user = await UserService.registrate_user(admin_data)

    print('===============ADMIN====USER=====WAS====CREATED====')
    new_user = await UserService.return_user_per_email("glison@example.com")
    print(new_user)



    initial_blockchain = await create_eth_blockchain()

    print('===============BLOCKCHAIN=====WAS====CREATED=======')
    print(initial_blockchain)
    print('====END========BLOCKCHAIN=====WAS====CREATED=======')
    initial_asset = await create_initial_asset(initial_blockchain)
    print('===============ASETH==========WAS====CREATED=======')
    print(initial_asset.id)
    print(initial_asset.code)
    print('====END========ASETH=========WAS====CREATED=======')
    print('*********END===OF====INITIALISATION===DATA*********')


async def create_eth_blockchain():
    blockchain = NewBlochainSchema(
        blockchain_type="eth_like",
        title="ethereum",
    )
    with open(f"seed/images/ethereum-icon.png", "rb") as photo:
        blockchain.photo = photo
        initial_blockchain = await BlockchainService.create_blockchain(blockchain)
    return initial_blockchain

async def create_initial_asset(initial_blockchain):
    new_asset_schema = NewAssetSchema(
        type='currency',
        text='ethereum_currency_asseth',
        decimal_places=18,
        title='ETH',
        code='ETH'
    )
    initial_asset = await AssetService.create_asset(new_asset_schema, initial_blockchain)
    return initial_asset


if __name__ == "__main__":
    asyncio.run(initialisation())
