from redis_config.redis_config import redis_connection
import ast
from src.wallets.services.wallet_etherium_service import WalletEtheriumService


class RedisParserService:
    def __init__(self) -> None:
        self.redis_connection = redis_connection

    async def link_sids_with_adress(self, sid, address):
        sid_list = await self.redis_connection.hget("wallet_sid_pair", address)
        match sid_list:
            case None:
                online_sid_list = [
                    sid,
                ]
                await self.redis_connection.hmset(
                    "wallet_sid_pair", mapping={address: str(online_sid_list)}
                )
            case byte:
                decoded_sid_list = ast.literal_eval(sid_list.decode())
                decoded_sid_list.append(sid)
                await self.redis_connection.hmset(
                    "wallet_sid_pair", mapping={address: str(decoded_sid_list)}
                )

    async def add_user_to_wallets_online(self, sid, all_users_wallets, user_id):
        await self.redis_connection.hmset(
            "profile_wallets_seed_user_pair", mapping={sid: user_id}
        )

        user_wallets_addresses = []
        for wallet_key in all_users_wallets:
            user_wallets_addresses.append(all_users_wallets[wallet_key]["address"])

            # new!
            await self.link_sids_with_adress(
                sid, all_users_wallets[wallet_key]["address"]
            )

        wallets_data = await self.redis_connection.hget(
            "profile_wallets_online", user_id
        )

        match wallets_data:
            case None:
                wallets_data_dict = {
                    "wallets_data": user_wallets_addresses,
                    "user_id": user_id,
                    "connection_quantity": 1,
                    "sid_list": [
                        sid,
                    ],
                }
                await self.redis_connection.hmset(
                    "profile_wallets_online", mapping={user_id: str(wallets_data_dict)}
                )

            case bytes:
                wallets_data_dict = ast.literal_eval(wallets_data.decode("utf-8"))
                wallets_data_dict["connection_quantity"] += 1
                sid_list = wallets_data_dict["sid_list"]
                match sid_list:
                    case None:
                        sid_list = [
                            sid,
                        ]
                    case list:
                        sid_list.append(sid)
                wallets_data_dict["sid_list"] = sid_list
                wallets_data_dict["wallets_data"] = user_wallets_addresses
                await self.redis_connection.hmset(
                    "profile_wallets_online", mapping={user_id: str(wallets_data_dict)}
                )

        users_online = await self.redis_connection.hgetall("profile_wallets_online")

        sid_online = await redis_connection.hgetall("profile_wallets_seed_user_pair")

        if len(sid_online) == 1:
            result = {"new_parser_status": "start"}
        else:
            result = {"new_parser_status": None}

        await self.redis_connection.close()
        return result

    # ============================================================================================================
    async def delete_user_from_wallets_online(self, sid):
        user_id = await self.return_user_id_per_sid_and_delete(sid)
        wallets_addresses = (
            await WalletEtheriumService.return_all_wallets_adresses_per_user_id(user_id)
        )

        for address in wallets_addresses:
            await self.disconnect_sid_from_address(address, sid)

        user_data = await self.redis_connection.hget("profile_wallets_online", user_id)
        user_data_dict = ast.literal_eval(user_data.decode("utf-8"))
        user_data_dict["connection_quantity"] -= 1

        if user_data_dict["connection_quantity"] <= 0:
            await self.redis_connection.hdel("profile_wallets_online", user_id)

        else:
            sid_list = user_data_dict["sid_list"]
            sid_list.remove(sid)
            user_data_dict["sid_list"] = sid_list
            await self.redis_connection.hmset(
                "profile_wallets_online", mapping={user_id: str(user_data_dict)}
            )
        await self.redis_connection.close()

    async def disconnect_sid_from_address(self, address, sid):
        sid_list = await self.redis_connection.hget("wallet_sid_pair", address)
        decoded_sid_list = ast.literal_eval(sid_list.decode())
        match len(decoded_sid_list):
            case 1:
                await self.redis_connection.hdel("wallet_sid_pair", address)
            case _:
                decoded_sid_list.remove(sid)
                await self.redis_connection.hmset(
                    "wallet_sid_pair", mapping={address: str(decoded_sid_list)}
                )

    async def return_user_id_per_sid_and_delete(self, sid):
        user_id = int(
            (await redis_connection.hmget("profile_wallets_seed_user_pair", sid))[0]
        )
        await redis_connection.hdel("profile_wallets_seed_user_pair", sid)
        await self.redis_connection.close()
        return user_id

    async def return_list_of_sids_per_address(self, address):
        sid_list = await self.redis_connection.hget("wallet_sid_pair", address)
        decoded_sid_list = ast.literal_eval(sid_list.decode())

        return decoded_sid_list


redis_parser_service = RedisParserService()
