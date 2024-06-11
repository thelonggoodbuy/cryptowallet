from src.orders.services.commodity_abstract_services import CommodityAbstractService
from src.orders.repository.commodity_eth_repository import commodity_eth_rep_link
from src.orders.schemas import CommoditySchema, ErrorResponse, ErrorSchema
from pydantic import ValidationError






class CommodityEthService(CommodityAbstractService):
   
   
   async def save_commodity(commodity_data):
      try:
         validated_data = CommoditySchema(**commodity_data)
         print('--->>>>>commodity data<<<<<-------')
         print(validated_data.model_dump())
         validated_dict = validated_data.model_dump()
         print('==================================')

         new_commodity = await commodity_eth_rep_link.save_commodity_in_db(validated_dict)
         commodity_dict = {}
         commodity_dict['title'] = new_commodity.title

         commodity_dict['address'] = new_commodity.wallet.address
         commodity_dict['currency'] = new_commodity.wallet.asset.code

         commodity_dict['price'] = new_commodity.price
         commodity_dict['id'] = new_commodity.id
         commodity_dict['photo'] = new_commodity.photo['url'][1:]

         print('commodity_dict: ')
         print(commodity_dict)

         return commodity_dict
      
      except ValidationError as e:
            print(e)
            print(e.errors())
            
            error_response = ErrorResponse(
                errors=[ErrorSchema(msg=err['msg']) for err in e.errors()]
            )
            return error_response.model_dump()


   async def return_all_commodities_for_list():
      all_commodities = await commodity_eth_rep_link.return_commodities_for_list()
      print('all_commodities is:')
      print(all_commodities)
      print('===================')
      all_commodities_list = []
      for commodity in all_commodities:
         print(commodity)
         commodity_dict = {}
         commodity_dict['id'] = commodity.id
         commodity_dict['title'] = commodity.title
         commodity_dict['address'] = commodity.wallet.address
         commodity_dict['currency'] = commodity.wallet.asset.code
         commodity_dict['price'] = commodity.price
         commodity_dict['photo'] = commodity.photo['url'][1:]
         all_commodities_list.append(commodity_dict)


      return all_commodities_list
   

   async def return_commodity_by_id(commodity_id):
      commodity = await commodity_eth_rep_link.return_commodity_by_id(commodity_id)
      return commodity
       

   # async def return_commodity_to_sockets():
