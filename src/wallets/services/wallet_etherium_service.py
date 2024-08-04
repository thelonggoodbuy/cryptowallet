from typing import Optional
from src.wallets.services.wallet_abstract_service import AbstractWalletService
from src.users.services.user_service import UserService
from src.wallets.models import Wallet

from eth_account import Account
from propan_config.router import return_new_wallet

from sqlalchemy.exc import IntegrityError

from src.wallets.repository.wallet_etherium_repository import wallet_eth_rep_link
from src.wallets.repository.asset_repository import asset_rep_link

from etherium_config.settings import w3_connection

from concurrent.futures import ThreadPoolExecutor


class WalletEtheriumService(AbstractWalletService):
    """
    Provides methods for creating and retrieving Ethereum wallets stored in the database,
    and synchronizing database wallets with accounts in the Ethereum blockchain.

    This service inherits from the abstract `AbstractWalletService` class and
    implements specific functionalities for Ethereum wallets. It handles tasks
    such as retrieving wallets for a user, creating new wallets, and importing
    existing wallets. It also interacts with the `etherium_crypro_scanner` to synchronize
    wallet transaction states if necessary.
    """

    async def return_wallets_per_user_email(email: str) -> dict:
        """
        Returns all wallets linked to a user.

        Args:
            email (str): The user's email (unique field in database).

        Returns:
            wallets_dict (dict): A dictionary containing information about the user's wallets,
                  including address, asset code, balance, and blockchain photo URL.
                  The response structure follows a Messaging pattern.
        """

        from crypto_scanner_service.services.eth_crypro_scanner import (
            etherium_crypro_scanner,
        )

        user = await UserService.return_user_per_email(email)
        wallets = await wallet_eth_rep_link.return_wallets_per_user(user)
        wallets_dict = {}
        for wallet in wallets:
            balance = await w3_connection.eth.get_balance(wallet.address)
            balance_in_ether = w3_connection.from_wei(balance, "ether")
            if balance_in_ether != wallet.balance:
                # here we syncronize wallet transactions in db and in web3 (!!!)
                wallet_data = {"current_wallet_adress": wallet.address}

                await etherium_crypro_scanner.synchronize_transaction_state_for_wallet(
                    wallet_data
                )

                wallet = await wallet_eth_rep_link.update_wallet_ballance(
                    wallet.id, balance_in_ether
                )

            wallets_dict[wallet.id] = {
                "address": wallet.address,
                "asset": wallet.asset.code,
                "balance": float(wallet.balance),
            }
            wallets_dict[wallet.id]["blockchain_photo"] = wallet.asset.blockchain.photo[
                "url"
            ][1:]
        # print('=======================>>>>>!!!!!<<<<<==============================')
        # print(wallet.asset.blockchain.photo)
        # print('====================================================================')
        return wallets_dict

    async def return_wallets_per_user_email_without_sync(email: str) -> dict:
        # TODO chage description
        """
        Returns all wallets linked to a user.

        Args:
            email (str): The user's email (unique field in database).

        Returns:
            wallets_dict (dict): A dictionary containing information about the user's wallets,
                  including address, asset code, balance, and blockchain photo URL.
                  The response structure follows a Messaging pattern.
        """

        # from crypto_scanner_service.services.eth_crypro_scanner import etherium_crypro_scanner

        user = await UserService.return_user_per_email(email)
        wallets = await wallet_eth_rep_link.return_wallets_per_user(user)
        wallets_dict = {}
        for wallet in wallets:
            # balance = await w3_connection.eth.get_balance(wallet.address)
            # balance_in_ether = w3_connection.from_wei(balance, 'ether')
            # if balance_in_ether != wallet.balance:
            #     # here we syncronize wallet transactions in db and in web3 (!!!)
            #     wallet_data = {'current_wallet_adress': wallet.address}

            #     await etherium_crypro_scanner.synchronize_transaction_state_for_wallet(wallet_data)

            #     wallet = await wallet_eth_rep_link.update_wallet_ballance(wallet.id, balance_in_ether)

            wallets_dict[wallet.id] = {
                "address": wallet.address,
                "asset": wallet.asset.code,
                "balance": float(wallet.balance),
            }
            wallets_dict[wallet.id]["blockchain_photo"] = wallet.asset.blockchain.photo[
                "url"
            ][1:]
        print('=======================>>>>>!!!!!<<<<<==============================')
        print(wallet.asset.blockchain.photo)
        print('====================================================================')
        return wallets_dict

    async def return_wallet_per_id(id: int) -> Optional[Wallet]:
        """
        Retreive wallet per id.

        Args:
            id (int) : The wallet id

        Returns:
            wallet (Wallet): wallet object from db.
        """
        wallet = await wallet_eth_rep_link.return_wallet_per_id(id)
        return wallet

    async def create_wallet_for_user(new_wallet_data: dict) -> dict:
        """
        Creates a new Ethereum wallet for a user.

        Args:
            new_wallet_data (dict): Form data received by sockets containing:
                - token (str): User's authentication token.
                - sid (str): Session identifier.

        Returns:
            new_wallet_dictionary (dict): A dictionary containing information about the created wallet,
                  including status, ID, address, asset code, blockchain photo URL,
                  and the provided session ID.
        """
        email = await UserService.return_email_by_token(token=new_wallet_data["token"])
        user = await UserService.return_user_per_email(email)
        asset = await asset_rep_link.return_asset_per_code(code="ETH")

        with ThreadPoolExecutor() as executor:
            future = executor.submit(w3_connection.eth.account.create)
            new_account = future.result()

        new_account_private_key = w3_connection.to_hex(new_account.key)
        new_wallet = await wallet_eth_rep_link.create_new_wallet(
            private_key=new_account_private_key,
            user=user,
            address=new_account.address,
            asset=asset,
        )

        new_wallet_dictionary = {
            "status": "success",
            "id": new_wallet.id,
            "address": new_wallet.address,
            "asset": new_wallet.asset.code,
            "blockchain_photo": new_wallet.asset.blockchain.photo["url"][1:],
            "room": new_wallet_data["room"],
            "balance": new_wallet.balance,
        }
        return new_wallet_dictionary

    async def import_wallet_for_user(wallet_data: dict) -> dict:
        """
        Imports an existing Ethereum account to the CryptoWallet,
        and create new wallet for it.

        If an error occurs, an appropriate error message is returned.


        Args:
            wallet_data(dict): Form data received by sockets containing:
                - token (str): User's authentication token.
                - private_key (str): Private key of the account to import.
                - sid (str): Session identifier.


        Returns:
            imported_wallet_dictionary(dict) : A dictionary
                containing information about the import process,
                including status, wallet details (on success), error message (on failure),
                and the provided session ID.

        """

        try:
            private_key = wallet_data["private_key"]
            account = Account.from_key(private_key)

            # Retrieve user and asset data
            email = await UserService.return_email_by_token(token=wallet_data["token"])
            user = await UserService.return_user_per_email(email)
            asset = await asset_rep_link.return_asset_per_code(code="ETH")

            # Get and format wallet balance
            balance = await w3_connection.eth.get_balance(account.address)
            balance_in_ether = w3_connection.from_wei(balance, "ether")

            # Create wallet in database
            import_wallet_private_key = w3_connection.to_hex(account.key)
            imported_wallet = await wallet_eth_rep_link.create_new_wallet(
                private_key=import_wallet_private_key,
                user=user,
                address=account.address,
                asset=asset,
                balance=balance_in_ether,
            )

            imported_wallet_dictionary = {
                "status": "success",
                "id": imported_wallet.id,
                "address": imported_wallet.address,
                "asset": imported_wallet.asset.code,
                "blockchain_photo": imported_wallet.asset.blockchain.photo["url"][1:],
                "balance": imported_wallet.balance,
                "room": wallet_data["room"],
                # "balance": imported_wallet.balance,
            }
            # await return_new_wallet(imported_wallet_dictionary)

        except IntegrityError:
            error_text = (
                "Аккаунт з таким приватним ключем вже зареєстрованний в системі"
            )
            imported_wallet_dictionary = {
                "status": "error",
                "text": error_text,
                "room": wallet_data["room"],
            }
            # await return_new_wallet(imported_wallet_dictionary)

        except Exception:
            error_text = "Помилка в приватному ключі"
            imported_wallet_dictionary = {
                "status": "error",
                "text": error_text,
                "room": wallet_data["room"],
            }
            # await return_new_wallet(imported_wallet_dictionary)

        from socketio_config.server import client_manager
        # TODO Emiter
        room = imported_wallet_dictionary["room"]
        await client_manager.emit(
            "show_new_wallet", room=room, data=imported_wallet_dictionary, namespace="/profile_wallets"
        )


    async def return_wallet_per_address(address: str) -> Wallet:
        """
        Retrieves a wallet object from the database based on its address.

        Args:
            address(str): The address of the wallet to retrieve.

        Returns:
            wallet(Wallet): wallet object from DB.
        """
        wallet = await wallet_eth_rep_link.return_wallet_per_address(address)
        return wallet

    async def return_all_wallets_addresses() -> dict:
        """
        Retrieves a dict of all Ethereum wallet addresses stored in the database.

        Returns:
            addresses_dict(dict): A dictionary containing all wallet addresses from the database,
            and structured by pair key - wallet_address, and value - user_id
        """
        addresses_dict = await wallet_eth_rep_link.return_all_wallets_addresses()
        return addresses_dict

    async def return_all_wallets_adresses_per_user_id(user_id: int) -> set:
        """
        Retrieves a set of Ethereum wallet addresses linked to a specific user.

        This function efficiently retrieves a set of strings representing wallet addresses
        associated with the provided user ID.

        Args:
            user_id(int): The ID of the user whose wallet addresses are needed.

        Returns:
            addresses_set(set):  A set containing all wallet addresses for the specified user.
        """
        addresses_set = (
            await wallet_eth_rep_link.return_all_wallets_adresses_per_user_id(user_id)
        )
        return addresses_set

    async def return_user_id_by_wallet_id(wallet_id):
        user_id = await wallet_eth_rep_link.return_user_id_by_wallet_id(wallet_id)
        return user_id

    @classmethod
    async def update_and_return_ballance_state(cls, wallet):
        # for wallet in wallets:

        balance = await w3_connection.eth.get_balance(wallet.address)
        print("----new---ballance----")
        print(balance)
        print("======================")
        print("----old---ballance----")
        print(wallet.balance)
        print("======================")
        balance_in_ether = w3_connection.from_wei(balance, "ether")
        if balance_in_ether != wallet.balance:
            # here we syncronize wallet transactions in db and in web3 (!!!)
            updated_wallet = await wallet_eth_rep_link.update_wallet_ballance(
                wallet.id, balance_in_ether
            )

        print("----balance-after-changeinc----")
        print(updated_wallet.balance)
        print("======================")

        return updated_wallet.balance
    
    @classmethod
    async def check_if_account_in_db(cls, account_address):
        account = await wallet_eth_rep_link.return_wallet_per_address(account_address)
        if account:
            return True
        else:
            return False


    @classmethod
    async def import_wallet_for_user_initial_script(cls, wallet_data: dict) -> dict:
        """
        
        Args:
            wallet_data(dict): Form data received by sockets containing:
                - user_id (int): User's id.
                - private_key (str): Private key of the account to import.

        """


        private_key = wallet_data["private_key"]
        account = Account.from_key(private_key)
        print('=====ACCOUNT DATA=====')
        print(account)
        print('======================')
        is_exist_account_in_db = await cls.check_if_account_in_db(account.address)
        if is_exist_account_in_db:
            result_dict = {'status': 'fail', 'error_text': 'wallet with this address already exist in db'}
        # Retrieve user and asset data
        # email = await UserService.return_email_by_token(token=wallet_data["token"])
        else:
            user = await UserService.return_user_object_by_id(wallet_data["user_id"])
            asset = await asset_rep_link.return_asset_per_code(code="ETH")

            # Get and format wallet balance
            balance = await w3_connection.eth.get_balance(account.address)
            balance_in_ether = w3_connection.from_wei(balance, "ether")

            # Create wallet in database
            import_wallet_private_key = w3_connection.to_hex(account.key)
            imported_wallet = await wallet_eth_rep_link.create_new_wallet(
                private_key=import_wallet_private_key,
                user=user,
                address=account.address,
                asset=asset,
                balance=balance_in_ether,
            )
            result_dict = {'status': 'success', 'address': imported_wallet.address}
        return result_dict





    # @classmethod
    # async def import_wallet_for_user_initial_script(cls, wallet_data: dict) -> dict:
    #     """
        
    #     Args:
    #         wallet_data(dict): Form data received by sockets containing:
    #             - user_id (int): User's id.
    #             - private_key (str): Private key of the account to import.

    #     """

    #     try:
    #         private_key = wallet_data["private_key"]
    #         account = Account.from_key(private_key)
    #         print('=====ACCOUNT DATA=====')
    #         print(account)
    #         print('======================')
    #         is_exist_account_in_db = await cls.check_if_account_in_db(account.address)
    #         if is_exist_account_in_db:
    #             result_dict = {'status': 'fail', 'error_text': 'wallet with this address already exist in db'}
    #         # Retrieve user and asset data
    #         # email = await UserService.return_email_by_token(token=wallet_data["token"])
    #         else:
    #             user = await UserService.return_user_object_by_id(wallet_data["user_id"])
    #             asset = await asset_rep_link.return_asset_per_code(code="ETH")

    #             # Get and format wallet balance
    #             balance = await w3_connection.eth.get_balance(account.address)
    #             balance_in_ether = w3_connection.from_wei(balance, "ether")

    #             # Create wallet in database
    #             import_wallet_private_key = w3_connection.to_hex(account.key)
    #             imported_wallet = await wallet_eth_rep_link.create_new_wallet(
    #                 private_key=import_wallet_private_key,
    #                 user=user,
    #                 address=account.address,
    #                 asset=asset,
    #                 balance=balance_in_ether,
    #             )
    #             result_dict = {'status': 'success', 'address': imported_wallet.address}


    #     except IntegrityError:
    #         error_text = "Аккаунт з таким приватним ключем вже зареєстрованний в системі"
    #         result_dict = {'status': 'fail', 'error_text': error_text}


    #     except Exception:
    #         error_text = "Помилка в приватному ключі"
    #         result_dict = {'status': 'fail', 'error_text': error_text}
        
    #     return result_dict