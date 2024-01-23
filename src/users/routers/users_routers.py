from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()






@router.get("/users/login/", response_class=HTMLResponse)
async def login():
    with open('front/login.html', 'r') as file:
        data = file.read()
    
    return HTMLResponse(content=data, status_code=200)



