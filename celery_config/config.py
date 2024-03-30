import time
from celery import Celery
from redis_config.redis_config import redis_url
from celery import shared_task
from src.wallets.data_adapters.db_services import return_wallets_per_user

from propan_config.router import add_update_wallet_list_query
# from socketio_config.server import update_wallet_state

from asgiref.sync import async_to_sync
import asyncio



app = Celery('celery_app', broker=redis_url)
app.conf.broker_url = redis_url
app.conf.result_backend = redis_url



# @app.task
@shared_task(queue="wallets_queue")
def monitoring_wallets_state_task(sid, email):
    wallet_dict = async_to_sync(return_wallets_per_user)(email)

    # print('--------wallet_dict-------')
    # print(wallet_dict)
    # print('-------------------------')

    update_wallet_data_message = {'walet_dict': wallet_dict, 'sid': sid}

    # add_update_wallet_list_query(update_wallet_data_message)

    async def body(update_wallet_data_message):
        print(update_wallet_data_message)
        await add_update_wallet_list_query(update_wallet_data_message)
    asyncio.run(body(update_wallet_data_message))

    time.sleep(60)

    monitoring_wallets_state_task(sid, email)