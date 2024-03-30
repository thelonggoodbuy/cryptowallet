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
    # ----------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------




    # print('--------')
    # print(tx_hash)
    # print('--------')

    # tx = w3_connection.eth.get_transaction(tx_hash)
    # trx_block_number = tx.blockNumber
    # # print(w3_connection.toHex(tx_hash))
    # print('transaction data')
    # print(tx)
    # print(trx_block_number)

    # # ---------------------------------->>>>>

    # # trx_unix_ts = w3_connection.eth.getBlock(trx_block_number).timestamp
    # status : int = -1
    # while True:
    #     try:
    #         '''
    #         https://web3py.readthedocs.io/en/stable/web3.eth.html#methods
    #         Returns the transaction receipt specified by transaction_hash. If the transaction has not yet been mined throws web3.exceptions.TransactionNotFound.
    #         If status in response equals 1 the transaction was successful. If it is equals 0 the transaction was reverted by EVM.
    #         '''
    #         trx_receipt = w3_connection.eth.getTransactionReceipt(tx_hash)

    #         status = trx_receipt['status']
    #         if status == 0 or status == 1:

    #             print('-----Transactions---receipt----')
    #             print(trx_receipt)
    #             print('-------------------------------')

    #             # logs_summary = []

    #             # from web3._utils.events import EventLogErrorFlags
    #             '''
    #             Note here, we are checking "Transfer" events! Not "Swap"! That's the confusing bit!
    #             '''
    #             # logs = pool_contract.events.Transfer().processReceipt(trx_receipt, EventLogErrorFlags.Warn)
    #             # for log in logs:
    #             #     transaction_type = log.event
    #             #     sender_address = log.args['from']
    #             #     destination_address = log.args['to']
    #             #     amount = log.args['value']

    #             #     logs_summary.append( {
    #             #         'transaction_type' : transaction_type,
    #             #         'sender_address' : sender_address,
    #             #         'destination_address' : destination_address,
    #             #         'amount' : amount
    #             #     })

    #             gas_used_in_units = trx_receipt['gasUsed']
    #             gas_price = w3_connection.eth.gasPrice
    #             gas_used_in_wei = gas_used_in_units * gas_price
    #             # gas_used_in_coin = gas_used_in_wei / (ONE_BILLION * ONE_BILLION)
    #             break
    #     except TransactionNotFound:
    #         # Transaction not found!
    #         pass

    #     trx_status : str = "Pending"
    #     if status==1:
    #         trx_status = "Confirmmed"
    #     elif status==0:
    #         trx_status = "Reverted"

    #     transaction_report : Dict = {
    #         'trx_hash' : tx_hash,
    #         'trx_block_number'  : trx_block_number,
    #         'status' : trx_status,
    #         # 'trx_unix_ts' : trx_unix_ts,
    #         'gas' : {
    #             'gas_used_in_units' : gas_used_in_units,
    #             'gas_price' : gas_price,
    #             'gas_used_in_wei' : gas_used_in_wei,
    #             # 'gas_used_in_coin' : gas_used_in_coin # On CRONOS, "Coin" refers to CRO. On Ethereum, this is ETH.
    #         },
    #         # 'logs' : logs_summary
    #     }

    #     print(transaction_report)