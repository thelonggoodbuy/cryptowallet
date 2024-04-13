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
from web3.exceptions import InvalidAddress

from src.etherium.repository.transaction_eth_repository import transaction_rep_link





class TransactionETHService(TransactionAbstractService):

    async def send_eth_to_account(account_data):

        if account_data['address'] == '':
            result = {'result': 'error', 'error_text': 'введіть адрессу отримувача'}

        elif account_data['value'] == '':
            result = {'result': 'error', 'error_text': 'введіть сумму для транзакції'}
        else:
            try:                
                await w3_connection.eth.get_balance(account_data['address'])

                receiver_address = account_data['address']
                current_wallet_id = account_data['current_wallet_id']
                curent_wallet = await WalletEtheriumService.return_wallet_per_id(id=current_wallet_id)
                sender_adress = curent_wallet.address
                value = account_data['value']
                
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
                # ***посмотреть как мы сохраняем транзакции которые отправленны***


                transaction = await transaction_rep_link.save_transaction_in_db(
                    send_from = sender_adress,
                    send_to = receiver_address,
                    value = value,
                    txn_hash = tx_hash.hex(),
                    status = "pending"
                )


                result = {'result': 'success', 
                          'error_text': '',
                          'type': 'sending_transaction',
                          'value': transaction.value,
                          'from': sender_adress,
                          }


            except InvalidAddress:
                result = {'result': 'error', 'error_text': 'помилка в адрессі отримувача'}


        return result
    

    async def return_all_transactions_per_wallet(wallet_adress):
        transactions = await transaction_rep_link.return_all_transactions_per_waller_address(wallet_adress)
        return transactions
    

    async def update_transaction(transaction_obj, transaction_new_data):
        await transaction_rep_link.update_transaction(transaction_obj, transaction_new_data)


    async def save_transaction(transaction_data_dict):
        # print('===1===')
        # print(transaction_data_dict)
        # print('=======')
        # print(transaction_data_dict['from'])

        # wallet = await WalletEtheriumService.return_wallet_per_address(transaction_data_dict['from'])

        # print('-----Wallet--obj-----')
        # print(wallet)
        # print(type(wallet))
        # print('---------------------')

        # print('===2===')
        # print(wallet)
        # print(type(wallet))
        # print('=======')
        # print('===2.1===')
        # print('...................................................................................................')
        from_web3_data_dict = {'date_time_transaction': transaction_data_dict['date_time_transaction'],
                               'txn_fee': transaction_data_dict['txn_fee']}
        # print('***')
        # print(from_web3_data_dict)
        # print(from_web3_data_dict['txn_fee']*1000000000000)
        # print(type(from_web3_data_dict['txn_fee']))
        # print(float(transaction_data_dict['txn_fee']))
        # print(type(float(from_web3_data_dict['txn_fee'])))
        # print('***')
        # print('...................................................................................................')

        await transaction_rep_link.save_transaction_in_db(send_from=transaction_data_dict['send_from'],
                                                          send_to=transaction_data_dict['send_to'],
                                                          value=w3_connection.from_wei(int(transaction_data_dict['value']), 'ether'),
                                                          txn_hash=transaction_data_dict['txn_hash'],
                                                          status=transaction_data_dict['status'],
                                                          from_web3_data_dict=from_web3_data_dict)