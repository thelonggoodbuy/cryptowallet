from src.etherium.services.transaction_abstract_service import TransactionAbstractService
from web3.exceptions import TransactionNotFound
from typing import Dict
from starlette.concurrency import run_in_threadpool
from web3 import Web3, AsyncWeb3
from web3.eth import AsyncEth
from concurrent.futures import ThreadPoolExecutor
from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from eth_account import Account

from etherium_config.settings import w3_connection







class TransTransactionETHService(TransactionAbstractService):

    async def send_eth_to_account(account_data):
        # w3_connection = Web3(AsyncWeb3.AsyncHTTPProvider("https://sepolia.infura.io/v3/245f010db1cf410f87552fb31909a726"), 
        #                     modules={'eth': (AsyncEth,)}, 
        #                     middlewares=[])



        receiver_address = account_data['address']
        value = account_data['value']
        current_wallet_id = account_data['current_wallet_id']
        curent_wallet = await WalletEtheriumService.return_wallet_per_id(id=current_wallet_id)

        sender_private_key = curent_wallet.private_key
        account_obj = Account.from_key(sender_private_key)

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