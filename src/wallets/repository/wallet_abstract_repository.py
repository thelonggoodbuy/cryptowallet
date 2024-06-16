from abc import ABC, abstractmethod


class WalletAbstractRepository(ABC):
    @abstractmethod
    async def return_wallets_per_user(user):
        raise NotImplementedError
