from celery import Celery
from redis_config.redis_config import redis_url
from datetime import timedelta


app = Celery("celery_app", broker=redis_url)
app.conf.broker_url = redis_url
app.conf.result_backend = redis_url


app.conf.task_routes = {
    "celery_config.tasks.test_beat": "test-queue",
    "celery_config.tasks.parse_latest_block_query": "parse_latest_block_query",
    "celery_config.tasks.handle_block": "handle_block_query",
    "celery_config.tasks.handle_oldest_delivery": "handle_oldest_delivery_query",
}


app.conf.beat_schedule = {
    "celery_beat_test_delivery": {
        "task": "celery_config.tasks.handle_oldest_delivery",
        "schedule": timedelta(seconds=5),
    }
}

app.autodiscover_tasks()
