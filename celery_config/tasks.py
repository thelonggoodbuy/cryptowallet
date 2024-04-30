from celery_config.config import app
from web3 import Web3
from functools import lru_cache 
from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from asgiref.sync import async_to_sync
from etherium_config.services.eth_parser import eth_parser_service
import asyncio


w3_connection = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/245f010db1cf410f87552fb31909a726"))




class BlockCache():
    current_block_number = None

    
@app.task
def parse_latest_block_query():
    block_number = w3_connection.eth.get_block('latest')['number']
    if BlockCache.current_block_number == None:
        BlockCache.current_block_number = block_number
        print('First block saved in cache')
    elif BlockCache.current_block_number == block_number:
        print('block NOT change')
        print(block_number)
    elif BlockCache.current_block_number != block_number:
        print('block CHANGED!')
        print(block_number)
        handle_block.delay(block_number)
        BlockCache.current_block_number = block_number



@app.task
def handle_block(block_number):
    block = w3_connection.eth.get_block(block_number)
    all_transactions = block.transactions
    loop = asyncio.get_event_loop()
    all_wallets_number_set = loop.run_until_complete(WalletEtheriumService.return_all_wallets_addresses())

    send_to = {}
    send_from = {}
    new_or_updated_transactions = set()
    

    for transaction_hash in all_transactions:
        transaction = w3_connection.eth.get_transaction(transaction_hash)
        if transaction['to'] in all_wallets_number_set:

            send_to[transaction_hash] = transaction['to']
            new_or_updated_transactions.add(transaction)

        if transaction['from'] in all_wallets_number_set:

            send_from[transaction_hash] = transaction['from']
            new_or_updated_transactions.add(transaction)

    loop.run_until_complete(eth_parser_service.update_transactions_from_parser(new_or_updated_transactions, send_to, send_from))