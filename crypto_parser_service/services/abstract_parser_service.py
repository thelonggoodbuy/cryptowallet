from abc import ABC, abstractmethod



class AbstractParserService(ABC):

    @abstractmethod
    async def parse_block():
        raise NotImplementedError
    
    @abstractmethod
    async def update_transactions_from_parser():
        raise NotImplementedError
