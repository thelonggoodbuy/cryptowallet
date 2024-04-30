run-dev-clear:
	clear
	uvicorn fastapi_config.main:app --reload
	# propan run -p 5672:5672 propan_config.app:app

run-dev:
	uvicorn fastapi_config.main:app --reload

# celery commands
# =============================================
run-dev-celery-block-parser-query:
	clear
	celery -A celery_config.tasks worker -l info -Q parse_latest_block_query --concurrency=1
	

run-dev-celery-block-handler-query:
	clear
	celery -A celery_config.tasks worker -l info -Q handle_block_query


run-dev-celery-schedule:
	clear
	celery -A celery_config.config beat -l info
# =============================================

