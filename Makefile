run-dev-clear:
	clear
	uvicorn fastapi_config.main:app --reload
	# propan run -p 5672:5672 propan_config.app:app

run-dev-celery-clear:
	clear
	celery -A celery_config.config worker -l info -Q wallets_queue
	

run-dev:
	uvicorn fastapi_config.main:app --reload