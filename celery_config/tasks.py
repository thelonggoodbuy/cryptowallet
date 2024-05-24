from celery_config.config import app
from web3 import Web3
from functools import lru_cache 
from crypto_parser_service.services.etherium_parser_service import ETHParserService
from asgiref.sync import async_to_sync
from etherium_config.services.eth_parser import eth_parser_service
import asyncio
import requests
from celery import chain


    
@app.task
def parse_latest_block_query():

    parser = ETHParserService()
    loop = asyncio.get_event_loop()
    block_number = loop.run_until_complete(parser.parse_block())


@app.task
def handle_block(block_number):

    loop = asyncio.get_event_loop()
    loop.run_until_complete(ETHParserService().handle_block(block_number))
    
