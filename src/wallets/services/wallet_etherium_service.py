from src.wallets.services.wallet_abstract_service import AbstractWalletService
from src.users.services.user_service import UserService
from eth_account import Account
from propan_config.router import return_new_wallet


# for refactoring
from sqlalchemy import select
from src.users.models import User
from src.wallets.models import Wallet, Asset
from web3 import Web3
from jose import JWTError, jwt
from sqlalchemy.exc import IntegrityError

from src.wallets.repository.wallet_etherium_repository import wallet_eth_rep_link
from src.wallets.repository.asset_repository import asset_rep_link

from etherium_config.settings import w3_connection


# w3_connection = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/245f010db1cf410f87552fb31909a726'))


from src.users.services.user_service import UserService
from concurrent.futures import ThreadPoolExecutor


class WalletEtheriumService(AbstractWalletService):


    async def return_wallets_per_user_email(email: str) -> dict:
        user = await UserService.return_user_per_email(email)
        wallets = await wallet_eth_rep_link.return_wallets_per_user(user)
        wallets_dict = {}
        for wallet in wallets:
            balance = await w3_connection.eth.get_balance(wallet.address)
            balance_in_ether = w3_connection.from_wei(balance, 'ether')
            if balance_in_ether != wallet.balance: 
                wallet = await wallet_eth_rep_link.update_wallet_ballance(wallet.id, balance_in_ether)

            wallets_dict[wallet.id] = {
                'address': wallet.address,
                'asset': wallet.asset.code,
                'balance':float(wallet.balance)
            }
            wallets_dict[wallet.id]['blockchain_photo'] = wallet.asset.blockchain.photo['url'][1:]
        return wallets_dict
    

    async def return_wallet_per_id(id: int) -> dict:
        wallet = await wallet_eth_rep_link.return_wallet_per_id(id)
        return wallet
       
    def create_account():
        return w3_connection.eth.account.create()

    async def create_wallet_for_user(new_wallet_data: dict) -> dict:
        email = await UserService.return_email_by_token(token = new_wallet_data['token'])
        user = await UserService.return_user_per_email(email)
        asset = await asset_rep_link.return_asset_per_code(code='ETH')

        with ThreadPoolExecutor() as executor:
            future = executor.submit(w3_connection.eth.account.create)
            new_account = future.result()

        new_account_private_key = w3_connection.to_hex(new_account.key)
        new_wallet = await wallet_eth_rep_link.create_new_wallet(private_key=new_account_private_key,
                                                                user=user,
                                                                address=new_account.address,
                                                                asset=asset)

        new_wallet_dictionary = {
                'status': 'success',
                'id': new_wallet.id,
                'address': new_wallet.address,
                'asset': new_wallet.asset.code, 
                'blockchain_photo': new_wallet.asset.blockchain.photo['url'][1:],
                'sid': new_wallet_data['sid']
        }
        return new_wallet_dictionary
    

    async def import_wallet_for_user(wallet_data):

        try:
            private_key = wallet_data['private_key']
            account = Account.from_key(private_key)
            email = await UserService.return_email_by_token(token = wallet_data['token'])
            user = await UserService.return_user_per_email(email)
            asset = await asset_rep_link.return_asset_per_code(code='ETH')

            balance = await w3_connection.eth.get_balance(account.address)
            balance_in_ether = w3_connection.from_wei(balance, 'ether')

            import_wallet_private_key = w3_connection.to_hex(account.key)

            imported_wallet = await wallet_eth_rep_link.create_new_wallet(private_key=import_wallet_private_key,
                                                                            user=user,
                                                                            address=account.address,
                                                                            asset=asset,
                                                                            balance=balance_in_ether)

            imported_wallet_dictionary = {
                'status': 'success',
                'id': imported_wallet.id,
                'address': imported_wallet.address,
                'asset': imported_wallet.asset.code, 
                'blockchain_photo': imported_wallet.asset.blockchain.photo['url'][1:],
                'balance': imported_wallet.balance,
                'sid': wallet_data['sid']
        }
            await return_new_wallet(imported_wallet_dictionary)


        except IntegrityError:
            error_text = 'Аккаунт з таким приватним ключем вже зареєстрованний в системі'
            imported_wallet_dictionary = {'status': 'error',
                                        'text': error_text,
                                        'sid': wallet_data['sid']}
            await return_new_wallet(imported_wallet_dictionary)

        except Exception as e:
            print(e)
            error_text = 'Помилка в приватному ключі'
            imported_wallet_dictionary = {'status': 'error',
                                        'text': error_text,
                                        'sid': wallet_data['sid']}
            await return_new_wallet(imported_wallet_dictionary)