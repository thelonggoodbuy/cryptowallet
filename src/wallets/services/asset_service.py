from src.wallets.repository.asset_repository import asset_rep_link
from src.wallets.schemas import NewAssetSchema
from src.wallets.models import Blockchain



class AssetService():

    @classmethod
    async def create_asset(cls, block_chain_data: NewAssetSchema, blockchain: Blockchain):
        asset = await asset_rep_link.create_asset(block_chain_data, blockchain)
        return asset