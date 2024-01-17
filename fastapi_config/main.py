from fastapi import Depends, FastAPI

from src.microservices.api_gateway_service.routers import api_gateway_routers


app = FastAPI()

app.include_router(api_gateway_routers.router)


@app.get("/")
async def root():
    return {"message": "Cryptowallet main app!"}