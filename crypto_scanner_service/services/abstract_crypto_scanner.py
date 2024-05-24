
from abc import ABC, abstractmethod


class AbstractCryproScanner(ABC):

    """
    Abstract class for asynchronously scanning transaction states in concrete wallets,
    synchronizing them with the state in the database, and formatting the results.
    """

    @abstractmethod
    async def return_all_transactions_by_wallet():
        """
        Retrieves all transactions associated with a specific wallet, 
        potentially from an external source (blockchain).
        """
        raise NotImplementedError

    @abstractmethod
    async def synchronize_transaction_state_for_wallet():
        """
        Synchronizes the transaction state between the external source (blockchain)
        and the database for a specific wallet. This method may involve identifying 
        new transactions or updating existing ones.
        """
        raise NotImplementedError


    @abstractmethod
    async def compare_current_transactions_with_saved():
        """
        Compares the current transactions retrieved 
        (potentially in `synchronize_transaction_state_for_wallet`)
        with the ones stored in the database for a 
        specific wallet.
        """
        raise NotImplementedError

    
    @abstractmethod
    async def format_all_transactions_per_wallet():
        """
        Formats all transactions (potentially including identified differences) 
        in a specific way for presentation or further processing(potentially for
        message broker).
        """
        raise NotImplementedError