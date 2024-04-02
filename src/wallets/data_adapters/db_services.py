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




from web3.exceptions import TransactionNotFound
from typing import Dict
from starlette.concurrency import run_in_threadpool
from web3 import Web3, AsyncWeb3
from web3.eth import AsyncEth
from concurrent.futures import ThreadPoolExecutor



async def send_eth_to_account(account_data):

    w3_connection = Web3(AsyncWeb3.AsyncHTTPProvider("https://sepolia.infura.io/v3/245f010db1cf410f87552fb31909a726"), 
                        modules={'eth': (AsyncEth,)}, 
                        middlewares=[])



    receiver_address = account_data['address']
    value = account_data['value']
    current_wallet_id = account_data['current_wallet_id']

    generator = get_db()
    session = next(generator)
    query = select(Wallet).filter(Wallet.id==current_wallet_id)
    curent_wallet = session.execute(query).scalars().first()

    sender_private_key = curent_wallet.private_key
    account_obj = Account.from_key(sender_private_key)
    print(sender_private_key)
    print()

    nonce = await w3_connection.eth.get_transaction_count(account_obj.address ,'pending')

    chain_id = await w3_connection.eth.chain_id

    gas_price = await w3_connection.eth.gas_price

    transaction = {
        "from": account_obj.address,
        "chainId": chain_id, 
        "nonce": nonce,
        "gas": 21000,
        "gasPrice": gas_price,
        "value": w3_connection.to_wei(value, 'ether'),
        "to": receiver_address
    }

    with ThreadPoolExecutor() as executor:
        future = executor.submit(w3_connection.eth.account.sign_transaction,\
                                    transaction_dict=transaction,\
                                    private_key=sender_private_key)
        # Ожидание результата и получение его
        signed = future.result()

    print('=====Future===result=====')
    print(signed)
    print('=========================')


    tx_hash = await w3_connection.eth.send_raw_transaction(signed.rawTransaction)
    tx = await w3_connection.eth.get_transaction(tx_hash)
    
    print('--------')
    print(tx_hash)
    print('--------')
    
    tx = await w3_connection.eth.get_transaction(tx_hash)
    # trx_block_number = tx.blockNumber
    
    print('transaction data')
    print(tx)
    print('block data')
