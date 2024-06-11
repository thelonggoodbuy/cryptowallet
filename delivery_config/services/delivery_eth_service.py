from delivery_config.services.delivery_abstract_service import DeliveryAbstractService
from delivery_config.schemas import OrderRequestSchema, OrderRequestAsyncValidator
from pydantic import ValidationError
import asyncio
from src.orders.services.order_eth_service import OrderEthService
from src.orders.schemas import UpdateOrderSchema, OrderEvent
from socketio_config.server import client_manager
import httpx




class DeliveryEthService(DeliveryAbstractService):

    event_handlers = []


    @classmethod
    def register_event_handler(cls, handler):
        cls.event_handlers.append(handler)


    @classmethod
    def trigger_event(cls, event: OrderEvent):
        for handler in cls.event_handlers:
            handler(event)


    @classmethod
    def handle_event(cls, event: OrderEvent):
        # Place your service logic here
        # print(f"Handling event with data: {event.data}")
        cls.try_to_start_delivery(event.order_dict)




    @staticmethod
    async def create_new_order(data):
        print('----new---service---')
        print(data['sending_data'])
        print('--------------------')
        try:
            validated_data = OrderRequestSchema(**data['sending_data'])
            await OrderRequestAsyncValidator.validate_order_data(validated_data.model_dump())
            print('===SUCESSS===WITH====ORDER====SCHEMA====')
            print(validated_data)
            print('========================================')
            await OrderEthService.save_new_order(validated_data)

            
        # TODO handling this error with result in browser
        except ValueError as e:
            print(e)


    @classmethod
    async def try_to_start_delivery(cls, order_dict):
        print('--->Now this is a delivery service<---')
        print(order_dict)
        print('--------------------------------------')
        trn_hash = list(order_dict.keys())[0]
        update_order_data = UpdateOrderSchema(
            order_id=order_dict[trn_hash]['id'],
            status='new',
            user_id=order_dict['user_id']
        )
        updated_order = await OrderEthService.update_order(update_order_data)
        user_id = order_dict['user_id']
        print('===UPDATE===ORDER=====')
        print(updated_order)
        print(updated_order.order_status)
        print('ROOM ID IS:')
        print(f'room_ibay_{user_id}')
        print('=====emiting!!!=======')

        data = {"status": "new",
                "title": updated_order.commodity.title,
                "trn_hash": updated_order.transaction.txn_hash,
                "cost": float(updated_order.commodity.price),
                "orders_time": (updated_order.date_time_transaction).isoformat(),
                "status": updated_order.order_status,
                "order_id": updated_order.id,
                "user_id": user_id}

        await client_manager.emit('receive_announcement_data',
                                    data=data,
                                    room=f'room_ibay_{user_id}',
                                    namespace='/ibay',
                                )
        
        # await cls.try_to_make_deliver(updated_order)
        from celery_config.tasks import handle_requests_to_test_delivery
        handle_requests_to_test_delivery.delay(data)

            
    @classmethod
    async def make_transaction_fail(cls, order_dict):
        update_order_data = UpdateOrderSchema(
            order_id=order_dict['order_id'],
            status='fail',
            user_id=order_dict['user_id']
        )
        failed_order_dict = await OrderEthService.update_order(update_order_data)
        user_id = failed_order_dict['user_id']
        await client_manager.emit('receive_announcement_data',
                                    data=failed_order_dict,
                                    room=f'room_ibay_{user_id}',
                                    namespace='/ibay',
                                )
        

    @classmethod
    async def send_delivery(cls, order_dict):
        update_order_data = UpdateOrderSchema(
            order_id=order_dict['order_id'],
            status='delivery',
            user_id=order_dict['user_id']
        )
        delivery_order_dict = await OrderEthService.update_order(update_order_data)

        user_id = update_order_data.user_id

        data = {"status": "delivery",
                "title": delivery_order_dict.commodity.title,
                "trn_hash": delivery_order_dict.transaction.txn_hash,
                "cost": float(delivery_order_dict.commodity.price),
                "orders_time": (delivery_order_dict.date_time_transaction).isoformat(),
                "status": delivery_order_dict.order_status,
                "order_id": delivery_order_dict.id,
                "user_id": user_id}

        await client_manager.emit('receive_announcement_data',
                                    data=data,
                                    room=f'room_ibay_{user_id}',
                                    namespace='/ibay',
                                )


    # @classmethod
    # async def send_delivery(order_dict):
    #      update_order_data = UpdateOrderSchema(
    #         order_id=order_dict['order_id'],
    #         status='delivery',
    #         user_id=order_dict['user_id']
    #     )
    #     await OrderEthService.update_order(update_order_data)
    
           