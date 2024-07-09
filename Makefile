run-dev-clear:
	clear
	# export CRYPTO_WALLET_ENV=local
	export USE_LOCAL_ENV=true && \
	uvicorn fastapi_config.main:app --reload

run-docker-clear:
	clear
	uvicorn fastapi_config.main:app --reload

run-dev:
	uvicorn fastapi_config.main:app --reload

# celery commands
# =============================================
# 1!
run-dev-celery-block-parser-query:
	clear
	celery -A celery_config.tasks worker -l info -Q parse_latest_block_query -n worker_1 --concurrency=1 --loglevel=info

# 2!
run-dev-celery-block-handler-query:
	clear
	celery -A celery_config.tasks worker -l info -Q handle_block_query -n worker_2 --concurrency=1 --loglevel=info

# 3!
run-handle_oldest_delivery_query:
	clear
	celery -A celery_config.tasks worker -l info -Q handle_oldest_delivery_query -n worker_3 --concurrency=2 --loglevel=info
	# celery -A celery_config.tasks worker --loglevel=info



run-dev-celery-schedule:
	clear
	celery -A celery_config.config beat -l info
# =============================================
