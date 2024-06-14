from celery_config.config import app
from web3 import Web3
from functools import lru_cache 
from crypto_parser_service.services.etherium_parser_service import ETHParserService
from asgiref.sync import async_to_sync
from etherium_config.services.eth_parser import eth_parser_service
import asyncio
import requests
from celery import chain
import httpx
from delivery_config.services.delivery_eth_service import DeliveryEthService

    
@app.task
def parse_latest_block_query():

    parser = ETHParserService()
    loop = asyncio.get_event_loop()
    block_number = loop.run_until_complete(parser.parse_block())


@app.task
def handle_block(block_number):

    loop = asyncio.get_event_loop()
    loop.run_until_complete(ETHParserService().handle_block(block_number))
    
from time import time, sleep
# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

@app.task
def handle_requests_to_test_delivery(updated_order):
    print('receive data from other task!')

    async def fetch(client, url, number):
        try:
            response = await client.get(url, follow_redirects=True)
            if response.status_code != 200:
                raise httpx.HTTPStatusError(
                    message=f"Non-200 status code: {response.status_code} for URL: {url}",
                    request=response.request,
                    response=response
                )
            return response.text
        
        except httpx.HTTPStatusError as exc:
            print(f"------>HTTP error occurred: {exc.response.status_code} for {exc.request.url!r}.<-----")
            raise exc  # Raise the exception to stop further processing
        
        except httpx.RequestError as exc:
            print(f"------>An error occurred while requesting {exc.request.url!r}.<-----")
            raise exc  # Raise the exception to stop further processing
        
        except httpx.HTTPError as exc:
            print(f"------>An error occurred while requesting {exc.request.url!r}.<-----")
            raise exc  # Raise the exception to stop further processing
        

    async def run_fetch(order_data):
        await asyncio.sleep(1)
        num_requests = 10000
        concurrency = 50

        # url = "https://www.google.com"
        url = "https://httpbin.org/get"

        async with httpx.AsyncClient() as client:
            start_time = time()
            tasks = [fetch(client, url, _) for _ in range(1, num_requests)]

            try:
                for i in range(0, num_requests, concurrency):
                    batch = tasks[i:i + concurrency]
                    await asyncio.gather(*batch)
                    await asyncio.sleep(0.1)

                await DeliveryEthService.send_delivery(order_data)
                

            except Exception as e:

                # await DeliveryEthService.send_delivery(order_data)  
                await  DeliveryEthService.make_transaction_fail(order_data)
                
            end_time = time()
            execution_time = end_time - start_time
            print(f"Total execution time: {execution_time} seconds")
            


    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_fetch(updated_order))



@app.task
def handle_oldest_delivery():
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(DeliveryEthService.handle_oldest_delivery())
#     print('receive data from other task!')

#     async def fetch(client, url, number):
#         try:
#             response = await client.get(url)
#             print(number)
#             return response.text
#         except httpx.RequestError as exc:
#             print(f"An error occurred while requesting {exc.request.url!r}.")

#     async def run_fetch(updated_order):
#         url = "https://www.google.com"
#         async with httpx.AsyncClient() as client:
#             tasks = [fetch(client, url, _) for _ in range(1, 10000)]
#             await asyncio.gather(*tasks)


#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(run_fetch(updated_order))
