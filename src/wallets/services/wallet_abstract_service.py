from abc import ABC, abstractmethod


class AbstractWalletService(ABC):
    @abstractmethod
    async def return_wallets_per_user(email: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def create_wallet_for_user(new_wallet_data: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    async def import_wallet_for_user(import_wallet_for_user: str) -> dict:
        raise NotImplementedError
