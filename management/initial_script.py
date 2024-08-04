import sys
import os



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.wallets.schemas import NewBlochainSchema, NewAssetSchema
from src.users.services.user_service import UserService
from src.users.schemas import NewUserModel
from src.wallets.services.blochain_service import BlockchainService
from src.wallets.services.asset_service import AssetService
from src.wallets.services.wallet_etherium_service import WalletEtheriumService

import asyncio



print('==================INITIAL====SCRIPT======START===============')

async def initialisation():
    print('=====>initialisation blockchain and asset<=====')


    initial_blockchain = await create_eth_blockchain()
    print('===============BLOCKCHAIN=====WAS====CREATED=======')
    # print(initial_blockchain)
    # print(initial_blockchain.photo)
    # print('====END========BLOCKCHAIN=====WAS====CREATED=======')
    initial_asset = await create_initial_asset(initial_blockchain)
    print('===============ASETH==========WAS====CREATED=======')
    # print(initial_asset.id)
    # print(initial_asset.code)
    # print('====END========ASETH=========WAS====CREATED=======')


    # print('=====>initialisation users and wallets<=====')
    print('==================INITIALISATION==ADMIN===USER===============')
    initial_admin_user = await UserService.check_if_admin_user_exist()
    # all_users = await UserService.return_all_users()

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
    print('============CREATING WALLETS FOR ADMIN USERS=============')
    admin_initial_wallet_addresses_list = []
    [admin_initial_wallet_addresses_list.append(address) for address in os.environ.get("ADMIN_INITIAL_WALLET_KEYS").split(",")]
    new_user = await UserService.return_user_per_email(admin_data.email)
    # print('***')
    # print(admin_initial_wallet_addresses_list)
    # print(user)
    # print('***')

    for address in admin_initial_wallet_addresses_list:
        new_wallet = await WalletEtheriumService.import_wallet_for_user_initial_script({"user_id":new_user.id, "private_key": address})


    print('==================INITIALISATION==SIMPLE===USER===============')
    initial_simple_user = await UserService.return_user_per_email('test_2@example.com')
    if initial_simple_user:
        print('=====>INITIAL USER WAS CREATED<=====')
    else:
        simple_user_data = NewUserModel(
            email = "test_2@example.com",
            username = "Test",
            password = "qL12!kR--5t",
            repeat_password="Sn12!kR)-2t",
            data_status = "validated",
            is_admin=False
        )
        user = await UserService.registrate_user(simple_user_data)
    print('===============SIMPLE====USER=====WAS====CREATED====')
    print('============CREATING WALLETS FOR SIMPLE USERS=============')
        # print('============CREATING WALLETS FOR ADMIN USERS=============')
    simple_initial_wallet_addresses_list = []
    [simple_initial_wallet_addresses_list.append(address) for address in os.environ.get("SIMPLE_INITIAL_WALLET_KEYS").split(",")]
    new_simple_user = await UserService.return_user_per_email(simple_user_data.email)
    # print('***')
    # print(admin_initial_wallet_addresses_list)
    # print(user)
    # print('***')

    for address in simple_initial_wallet_addresses_list:
        new_wallet = await WalletEtheriumService.import_wallet_for_user_initial_script({"user_id":new_simple_user.id, "private_key": address})

    # print('created wallet')
    # print(new_wallet)
    # print(new_wallet.id)
    # print(new_wallet.address)






    print('*********END===OF====INITIALISATION===DATA*********')


async def create_eth_blockchain():
    blockchain = NewBlochainSchema(
        blockchain_type="eth_like",
        title="ethereum",
    )
    with open(f"seed/images/ethereum-icon.png", "rb") as photo:
        blockchain.photo = photo
        # print('=====PHOTO DATA======')
        # print(photo)
        # print('=====================')
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
