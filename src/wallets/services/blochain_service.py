from pydantic import BaseModel
from src.wallets.repository.blokchain_repository import blockchain_rep_link
from src.wallets.schemas import NewBlochainSchema



class BlockchainService():

    @classmethod
    async def create_blockchain(cls, block_chain_data: NewBlochainSchema):
        blockchain = await blockchain_rep_link.create_blockchain(block_chain_data)
        return blockchain
