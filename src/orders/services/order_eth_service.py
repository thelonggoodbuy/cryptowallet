from src.orders.services.order_abstract_service import OrderAbstractService
from src.orders.repository.order_eth_repository import order_eth_rep_link
from src.orders.repository.commodity_eth_repository import commodity_eth_rep_link
from src.orders.schemas import CommoditySchema, ErrorResponse, ErrorSchema
from pydantic import ValidationError

from delivery_config.schemas import OrderRequestSchema
from src.etherium.services.transaction_eth_service import TransactionETHService
from src.orders.services.commodity_eth_service import CommodityEthService
from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from src.orders.schemas import UpdateOrderSchema

class OrderEthService(OrderAbstractService):
   
   @classmethod
   async def save_new_order(cls, order_data: OrderRequestSchema):
      print('--->validated_data<---')
      print(order_data)
      print('----------------------')
      transaction = await cls.format_data_and_send_eth_to_account(order_data)
      commodity = await commodity_eth_rep_link.return_commodity_by_id(order_data.accomodation_id)
      print('Transaction in ordering!')
      print(transaction)
      
      print('Commodity in ordering!')
      print(commodity)
      print('=======================')
      order = await order_eth_rep_link.create_new_order_for_pending_transaction(transaction, commodity)
      print('New order exist!!!')
      print(order)
      print('=======================')

      
      

   @classmethod
   async def format_data_and_send_eth_to_account(cls, validated_data: OrderRequestSchema):

      accomodation = await CommodityEthService.return_commodity_by_id(validated_data.accomodation_id)
      # customer_wallet = await WalletEtheriumService.return_wallet_per_id(validated_data.wallet_id)

      # print('===>accomodation<===')
      # print(accomodation.price)
      print('===data===for===sending===')
      account_data = {}
      account_data['address'] = accomodation.wallet.address
      account_data['value'] = accomodation.price
      account_data['current_wallet_id'] = validated_data.wallet_id

      print('***')
      print(account_data)
      print('***')

      save_transaction_dict = await TransactionETHService.send_eth_to_account(account_data)
      transaction_id = save_transaction_dict['id']
      transaction = await TransactionETHService.return_transaction_by_id(transaction_id)
      return transaction


   @classmethod
   async def return_orders_tied_with_pending_transactions(cls):
      orders = await order_eth_rep_link.return_orders_tied_with_pending_transactions()
      order_dict = {}
      for order in orders:
         order_dict[order.transaction.txn_hash] = {
            'id': order.id,
            'datatime': order.date_time_transaction
         }

      return order_dict
   


   # @classmethod
   # async def return_single_orders_tied_with_pending_objects(cls, order_id):


   @classmethod
   async def update_order(cls, update_order_dеtail: UpdateOrderSchema):
      match update_order_dеtail.status:
         case 'new':
            updated_order = await order_eth_rep_link.update_status_order(update_order_dеtail)
         case 'fail':
            updated_order = await cls.make_fail_or_return(update_order_dеtail)
         case 'delivery':
            updated_order = await order_eth_rep_link.update_status_order(update_order_dеtail)

      return updated_order
   

   @classmethod
   async def make_fail_or_return(cls, update_order_dеtail: UpdateOrderSchema):
      order = await order_eth_rep_link.return_order_tied_with_pending_objects(update_order_dеtail.order_id)

      revert_tax = float(order.transaction.txn_fee) * 2.5
      revert_value = float(order.transaction.value) - revert_tax

      receiver_wallet = await WalletEtheriumService.return_wallet_per_address(order.transaction.send_to)

      revert_transaction_data = {'address': order.transaction.send_from, 
                                 'value': revert_value, 
                                 'current_wallet_id': receiver_wallet.id}
      
      revert_transaction = await TransactionETHService.send_eth_to_account(revert_transaction_data)
      update_order_dеtail.status = update_order_dеtail.status
      update_order_dеtail.return_transaction_id = revert_transaction['id']
      

      print('=================>>>>> You have send revert transaction! <<<<<<<<<================')
      print(revert_transaction)
      print('==================================================================================')
      
      updated_order = await order_eth_rep_link.update_status_order(update_order_dеtail)

      order_data = {"status": "fail",
                "title": updated_order.commodity.title,
                "trn_hash": updated_order.transaction.txn_hash,
                "cost": float(updated_order.commodity.price),
                "orders_time": (updated_order.date_time_transaction).isoformat(),
                "status": updated_order.order_status,
                "order_id": updated_order.id,
                "user_id": update_order_dеtail.user_id,
                "revert_transaction": revert_transaction['txn_hash']}

      return order_data


      # updated_order = await order_eth_rep_link.update_status_order(update_order_datail)


   
