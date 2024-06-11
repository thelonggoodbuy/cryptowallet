from abc import ABC, abstractmethod




class DeliveryAbstractService(ABC):

    @abstractmethod
    async def save_commodity_in_db():
        pass