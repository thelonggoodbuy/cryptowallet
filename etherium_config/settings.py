from web3 import Web3, AsyncWeb3
from web3.eth import AsyncEth





w3_connection = Web3(AsyncWeb3.AsyncHTTPProvider("https://sepolia.infura.io/v3/245f010db1cf410f87552fb31909a726"), 
                    modules={'eth': (AsyncEth,)}, 
                    middlewares=[])
    

