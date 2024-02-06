run-dev-clear:
	clear
	uvicorn fastapi_config.main:app --reload

run-dev:
	uvicorn fastapi_config.main:app --reload