from fastapi import APIRouter




router = APIRouter()



@router.get("/users/")
async def api_users():
    return [{"app": "users app"}]