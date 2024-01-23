from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from starlette.responses import FileResponse 


router = APIRouter()






@router.get("/users/login/", response_class=HTMLResponse)
# @router.get("/users/login/")
async def login():

    with open('front/login.html', 'r') as file:
        data = file.read()
    # print(data)

    # login_html = '/static/'

    # return [{"app": "users app", "page": "login page"}]

    
    return HTMLResponse(content=data, status_code=200)

    # return FileResponse('front/login.html')