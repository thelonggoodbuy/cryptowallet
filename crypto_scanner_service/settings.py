from web3 import Web3, AsyncWeb3
from web3.eth import AsyncEth

from aioetherscan import Client as AiotherscanClient
from aiohttp_retry import ExponentialRetry
from asyncio_throttle import Throttler
import os



# web3 py settings
HTTPS_SEPOLIA_INFURA_LINK = os.environ.get('HTTPS_SEPOLIA_INFURA_LINK')
ETHERSCAN_API_KEY = os.environ.get('ETHERSCAN_API_KEY')



w3_connection = Web3(
    AsyncWeb3.AsyncHTTPProvider(
        HTTPS_SEPOLIA_INFURA_LINK
    ),
    modules={"eth": (AsyncEth,)},
    middlewares=[],
)


def aiotherscan_client_executor(async_func):
    async def wrapper(*args, **kwargs):
        throttler = Throttler(rate_limit=1, period=6.0)
        retry_options = ExponentialRetry(attempts=2)
        aiotherscan_client = AiotherscanClient(
            ETHERSCAN_API_KEY,
            network="sepolia",
            throttler=throttler,
            retry_options=retry_options,
        )

        try:
            return await async_func(aiotherscan_client, *args, **kwargs)
        except Exception as e:
            print("An exception occurred:", type(e).__name__)
            print(e)
        finally:
            await aiotherscan_client.close()

    return wrapper
