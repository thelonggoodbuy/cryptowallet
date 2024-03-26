from src.wallets.models import Wallet, Asset
from src.users.models import User
from db_config.database import get_db
from sqlalchemy import select

from web3 import Web3

from propan_config.router import return_new_wallet
from eth_account import Account
from sqlalchemy.exc import IntegrityError




w3_connection = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/245f010db1cf410f87552fb31909a726'))
SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
ALGORITHM = "HS256"
from jose import JWTError, jwt


# return exist wallets from database
async def return_wallets_per_user(email):
    generator = get_db()
    session = next(generator)
    query = select(User).filter(User.email==email)
    user = session.execute(query).scalars().first()

    # print('----User want----')
    # print(user)
    # print('------------------')

    query = select(Wallet).filter(Wallet.user==user)
    wallets = session.execute(query).scalars().all()

    # print('----User want----')
    for wallet in wallets: 
        # print(wallet.id)
        balance = w3_connection.eth.get_balance(wallet.address)
        balance_in_ether = w3_connection.from_wei(balance, 'ether')
        print('-----')
        print(f'adress: {wallet.address}')
        print('balance in ETH:')
        print(balance_in_ether)
        print('------------------')
        if balance_in_ether != wallet.balance: 
            wallet.balance = balance_in_ether
            # wallet.commit()

            session.add(wallet)
        session.commit()


    wallets_dict = {}
    for wallet in wallets:
        wallets_dict[wallet.id] = {
            'address': wallet.address,
            'asset': wallet.asset.code,
            'balance':float(wallet.balance)
        }
        wallets_dict[wallet.id]['blockchain_photo'] = wallet.asset.blockchain.photo['url'][1:]

    return wallets_dict



async def create_wallet_for_user(new_wallet_data):

    token = new_wallet_data['token']
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")

    generator = get_db()
    session = next(generator)
    query = select(User).filter(User.email==email)
    user = session.execute(query).scalars().first()

    query = select(Asset).filter(Asset.code=='ETH')
    asset = session.execute(query).scalars().first()

    new_account = w3_connection.eth.account.create()

    new_wallet = Wallet(private_key=w3_connection.to_hex(new_account.key),
                       user=user,
                       address=new_account.address,
                       balance=0,
                       asset=asset
                       ) 

    session.add(new_wallet)
    session.commit()

    new_wallet_dictionary = {
            'status': 'success',
            'id': new_wallet.id,
            'address': new_wallet.address,
            'asset': new_wallet.asset.code, 
            'blockchain_photo': new_wallet.asset.blockchain.photo['url'][1:],
            'sid': new_wallet_data['sid']
    }

    print('-----New---wallet-----')
    print(new_wallet_dictionary)
    await return_new_wallet(new_wallet_dictionary)



async def import_wallet_for_user(import_wallet_for_user):
    # print('+++')
    # print('ballance is:')
    # balance = w3_connection.eth.get_balance('0xd3CdA913deB6f67967B99D67aCDFa1712C293601')
    # print(balance)
    # print(type(balance))
    # print('+++')

    try:
        private_key = import_wallet_for_user['private_key']
        account= Account.from_key(private_key)

        token = import_wallet_for_user['token']
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        generator = get_db()
        session = next(generator)
        query = select(User).filter(User.email==email)
        user = session.execute(query).scalars().first()

        query = select(Asset).filter(Asset.code=='ETH')
        asset = session.execute(query).scalars().first()

        balance = w3_connection.eth.get_balance(account.address)
        balance_in_ether = w3_connection.from_wei(balance, 'ether')

        imported_wallet = Wallet(private_key=private_key,
                        user=user,
                        address=account.address,
                        balance=balance_in_ether,
                        asset=asset
                        ) 

        session.add(imported_wallet)
        session.commit()

        imported_wallet_dictionary = {
            'status': 'success',
            'id': imported_wallet.id,
            'address': imported_wallet.address,
            'asset': imported_wallet.asset.code, 
            'blockchain_photo': imported_wallet.asset.blockchain.photo['url'][1:],
            'balance': imported_wallet.balance,
            'sid': import_wallet_for_user['sid']
    }
        await return_new_wallet(imported_wallet_dictionary)


    except IntegrityError:
        # print('Аккаунт з таким приватним ключем вже зареєстрованний в системі')
        error_text = 'Аккаунт з таким приватним ключем вже зареєстрованний в системі'
        imported_wallet_dictionary = {'status': 'error',
                                    'text': error_text,
                                    'sid': import_wallet_for_user['sid']}
        await return_new_wallet(imported_wallet_dictionary)

    except Exception as e:
        print(e)
        error_text = 'Помилка в приватному ключі'
        imported_wallet_dictionary = {'status': 'error',
                                    'text': error_text,
                                    'sid': import_wallet_for_user['sid']}
        await return_new_wallet(imported_wallet_dictionary)