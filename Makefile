run-dev-clear:
	clear
	uvicorn fastapi_config.main:app --reload
	# propan run -p 5672:5672 propan_config.app:app

run-dev:
	uvicorn fastapi_config.main:app --reload