from abc import ABC, abstractmethod




class CommodityAbstractRepository(ABC):

    @abstractmethod
    async def save_commodity_in_db():
        pass