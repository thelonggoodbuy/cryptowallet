from delivery_config.services.delivery_abstract_service import DeliveryAbstractService
from delivery_config.schemas import OrderRequestSchema, OrderRequestAsyncValidator
from src.orders.services.order_eth_service import OrderEthService
from src.orders.schemas import UpdateOrderSchema, OrderEvent

# from socketio_config.server import client_manager
import random
from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from src.orders.schemas import ErrorResponse, ErrorSchema


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
        try:
            validated_data = OrderRequestSchema(**data["sending_data"])
            await OrderRequestAsyncValidator.validate_order_data(
                validated_data.model_dump()
            )
            await OrderEthService.save_new_order(validated_data)

            print("--->validated data for order<---")
            print(validated_data)
            print("--------------------------------")
            return {"status": "success"}

        # TODO handling this error with result in browser
        except ValueError as e:
            print(e)
            error_response = ErrorResponse(
                errors=[
                    ErrorSchema(msg=err["msg"], field=err["loc"][0])
                    for err in e.errors()
                ]
            )
            return error_response.model_dump()
            # return {'status': e}

    @classmethod
    async def try_to_start_delivery(cls, order_dict):
        from socketio_config.server import client_manager

        print("--->Now this is a delivery service<---")
        print(order_dict)
        print("--------------------------------------")
        trn_hash = list(order_dict.keys())[0]
        update_order_data = UpdateOrderSchema(
            order_id=order_dict[trn_hash]["id"],
            status="new",
            user_id=order_dict["user_id"],
        )
        updated_order = await OrderEthService.update_order(update_order_data)
        user_id = order_dict["user_id"]
        print("===UPDATE===ORDER=====")
        print(updated_order)
        print(updated_order.order_status)
        print("ROOM ID IS:")
        print(f"room_ibay_{user_id}")
        print("=====emiting!!!=======")

        data = {
            "status": "new",
            "title": updated_order.commodity.title,
            "trn_hash": updated_order.transaction.txn_hash,
            "cost": float(updated_order.commodity.price),
            "orders_time": (updated_order.date_time_transaction).isoformat(),
            "order_id": updated_order.id,
            "user_id": user_id,
            "commodity_id": updated_order.commodity.id,
        }
        if updated_order.commodity.photo:
            data["photo"] = updated_order.commodity.photo["url"][1:]

        await client_manager.emit(
            "receive_announcement_data",
            data=data,
            room=f"room_ibay_{user_id}",
            namespace="/ibay",
        )

        # await cls.try_to_make_deliver(updated_order)
        from celery_config.tasks import handle_requests_to_test_delivery

        handle_requests_to_test_delivery.delay(data)

    @classmethod
    async def make_transaction_fail(cls, order_dict):
        from socketio_config.server import client_manager

        update_order_data = UpdateOrderSchema(
            order_id=order_dict["order_id"],
            status="fail",
            user_id=order_dict["user_id"],
        )
        failed_order_dict = await OrderEthService.update_order(update_order_data)
        user_id = failed_order_dict["user_id"]
        await client_manager.emit(
            "receive_announcement_data",
            data=failed_order_dict,
            room=f"room_ibay_{user_id}",
            namespace="/ibay",
        )

    @classmethod
    async def send_delivery(cls, order_dict):
        from socketio_config.server import client_manager

        update_order_data = UpdateOrderSchema(
            order_id=order_dict["order_id"],
            status="delivery",
            user_id=order_dict["user_id"],
        )
        delivery_order_dict = await OrderEthService.update_order(update_order_data)

        user_id = update_order_data.user_id

        data = {
            "status": "delivery",
            "title": delivery_order_dict.commodity.title,
            "trn_hash": delivery_order_dict.transaction.txn_hash,
            "cost": float(delivery_order_dict.commodity.price),
            "orders_time": (delivery_order_dict.date_time_transaction).isoformat(),
            "order_id": delivery_order_dict.id,
            "user_id": user_id,
            "commodity_id": delivery_order_dict.commodity.id,
        }

        await client_manager.emit(
            "receive_announcement_data",
            data=data,
            room=f"room_ibay_{user_id}",
            namespace="/ibay",
        )

    @classmethod
    async def handle_oldest_delivery(cls):
        print("***")
        print(
            "=====>>>DELIVERY DELIVERY DELIVERY DELIVERY DELIVERY DELIVERY DELIVERY DELIVERY DELIVERY DELIVERY DELIVERY DELIVERY <<<====="
        )
        print("***")
        from socketio_config.server import client_manager

        delivery_order = await OrderEthService.get_oldest_delidery()
        # delivery_change = random.choice([True, False])
        delivery_change = random.choice([False, True])

        # if delivery_order and delivery_change == True:
        if delivery_order and delivery_change:
            sender_wallet_address = delivery_order.transaction.send_from
            sender_wallet = await WalletEtheriumService.return_wallet_per_address(
                sender_wallet_address
            )
            update_order_data = UpdateOrderSchema(
                order_id=delivery_order.id,
                status="complete",
                user_id=sender_wallet.user_id,
            )

            order_result = await OrderEthService.update_order(update_order_data)

            data = {
                # "status": "complete",
                "title": order_result.commodity.title,
                "trn_hash": order_result.transaction.txn_hash,
                "cost": float(order_result.commodity.price),
                "orders_time": (order_result.date_time_transaction).isoformat(),
                "status": order_result.order_status,
                "order_id": order_result.id,
                "user_id": sender_wallet.user_id,
                "commodity_id": order_result.commodity.id,
            }

            if order_result.commodity.photo:
                data["photo"] = order_result.commodity.photo["url"][1:]

            user_id = sender_wallet.user_id
            await client_manager.emit(
                "receive_announcement_data",
                data=data,
                room=f"room_ibay_{user_id}",
                namespace="/ibay",
            )

        # elif delivery_order and delivery_change == False:
        elif delivery_order and not delivery_change:
            from socketio_config.server import client_manager

            # print('***')
            # print('=====>>>DELIBERY IS FALLSE!!!<<<=====')
            # print('***')
            # TODO returning!!!!
            sender_wallet_address = delivery_order.transaction.send_from
            sender_wallet = await WalletEtheriumService.return_wallet_per_address(
                sender_wallet_address
            )
            update_order_data = UpdateOrderSchema(
                order_id=delivery_order.id,
                status="returning",
                user_id=sender_wallet.user_id,
            )
            order_result = await OrderEthService.update_order(update_order_data)

            print("<<<=====================>>>")
            print(order_result)
            print("<<<=====================>>>")

            data = {
                "title": order_result["title"],
                "trn_hash": order_result["trn_hash"],
                "cost": float(order_result["cost"]),
                "orders_time": order_result["orders_time"],
                "status": order_result["status"],
                "order_id": order_result["order_id"],
                "user_id": sender_wallet.user_id,
                "commodity_id": order_result["commodity_id"],
            }

            if order_result.commodity.photo:
                data["photo"] = order_result.commodity.photo["url"][1:]

            user_id = sender_wallet.user_id
            await client_manager.emit(
                "receive_announcement_data",
                data=data,
                room=f"room_ibay_{user_id}",
                namespace="/ibay",
            )

        else:
            print("***")
            print("=====>>>There arent any requests to delivery<<<=====")
            print("***")

            # print('There are any new deliveys!')

    #      update_order_data = UpdateOrderSchema(
    #         order_id=order_dict['order_id'],
    #         status='delivery',
    #         user_id=order_dict['user_id']
    #     )
    #     await OrderEthService.update_order(update_order_data)
