from fastapi import APIRouter




router = APIRouter()



@router.get("/api_gateway/")
async def api_gateway():
    return [{"app": "this is api_gateway"}]