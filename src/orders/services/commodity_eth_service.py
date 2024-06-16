from src.orders.services.commodity_abstract_services import CommodityAbstractService
from src.orders.repository.commodity_eth_repository import commodity_eth_rep_link
from src.orders.schemas import CommoditySchema, ErrorResponse, ErrorSchema
from pydantic import ValidationError
from src.wallets.services.wallet_etherium_service import WalletEtheriumService


class CommodityEthService(CommodityAbstractService):
    async def save_commodity(commodity_data):
        try:
            validated_data = CommoditySchema(**commodity_data)
            print("--->>>>>commodity data<<<<<-------")
            print(validated_data.model_dump())
            validated_dict = validated_data.model_dump()
            print("==================================")

            new_commodity = await commodity_eth_rep_link.save_commodity_in_db(
                validated_dict
            )
            commodity_dict = {}
            commodity_dict["title"] = new_commodity.title

            commodity_dict["address"] = new_commodity.wallet.address
            commodity_dict["currency"] = new_commodity.wallet.asset.code

            commodity_dict["price"] = new_commodity.price
            commodity_dict["id"] = new_commodity.id
            commodity_dict["photo"] = new_commodity.photo["url"][1:]

            if new_commodity.wallet.address in commodity_data["users_wallet_owning"]:
                commodity_dict["is_owning_by_current_user"] = True
            else:
                commodity_dict["is_owning_by_current_user"] = False

            print("commodity_dict: ")
            print(commodity_dict)

            return commodity_dict

        except ValidationError as e:
            print(e)
            print(e.errors())

            error_response = ErrorResponse(
                errors=[
                    ErrorSchema(msg=err["msg"], field=err["loc"][0])
                    for err in e.errors()
                ]
            )
            return error_response.model_dump()

    async def return_all_commodities_for_list(user_id):
        all_commodities = await commodity_eth_rep_link.return_commodities_for_list()
        print("all_commodities is:")
        print(all_commodities)
        all_users_wallets_addresses = (
            await WalletEtheriumService.return_all_wallets_adresses_per_user_id(user_id)
        )
        print("all users wallets:")
        print(all_users_wallets_addresses)
        print("===================")
        all_commodities_list = []
        for commodity in all_commodities:
            print(commodity)
            commodity_dict = {}
            commodity_dict["id"] = commodity.id
            commodity_dict["title"] = commodity.title
            commodity_dict["address"] = commodity.wallet.address
            commodity_dict["currency"] = commodity.wallet.asset.code
            commodity_dict["price"] = commodity.price
            commodity_dict["photo"] = commodity.photo["url"][1:]
            if commodity.wallet.address in all_users_wallets_addresses:
                commodity_dict["is_owning_by_current_user"] = True
            else:
                commodity_dict["is_owning_by_current_user"] = False
            all_commodities_list.append(commodity_dict)

        return all_commodities_list

    async def return_commodity_by_id(commodity_id):
        commodity = await commodity_eth_rep_link.return_commodity_by_id(commodity_id)
        return commodity

    # async def return_commodity_to_sockets():
