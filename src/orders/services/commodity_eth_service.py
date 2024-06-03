from src.orders.services.commodity_abstract_services import CommodityAbstractService
from src.orders.repository.commodity_eth_repository import commodity_eth_rep_link

class CommodityEthService(CommodityAbstractService):
    

   async def save_commodity(commodity_data):
      new_commodity = await commodity_eth_rep_link.save_commodity_in_db(commodity_data)
      commodity_dict = {}
      commodity_dict['title'] = new_commodity.title

      commodity_dict['address'] = new_commodity.wallet.address
      commodity_dict['currency'] = new_commodity.wallet.asset.code

      commodity_dict['price'] = new_commodity.price
      commodity_dict['photo'] = new_commodity.photo['url'][1:]
      return commodity_dict


   async def return_all_commodities_for_list():
      all_commodities = await commodity_eth_rep_link.return_commodities_for_list()
      print('all_commodities is:')
      print(all_commodities)
      print('===================')
      all_commodities_list = []
      for commodity in all_commodities:
         print(commodity)
         commodity_dict = {}
         commodity_dict['title'] = commodity.title
         commodity_dict['address'] = commodity.wallet.address
         commodity_dict['currency'] = commodity.wallet.asset.code
         commodity_dict['price'] = commodity.price
         commodity_dict['photo'] = commodity.photo['url'][1:]
         all_commodities_list.append(commodity_dict)


      return all_commodities_list
   

   # async def return_commodity_to_sockets():
