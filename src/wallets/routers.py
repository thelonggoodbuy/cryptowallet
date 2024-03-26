from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from typing import Annotated, Optional
from src.users.models import User
from fastapi import Depends
from src.users.routers import get_current_user, UserInDB
from starlette.responses import RedirectResponse




router = APIRouter()


@router.get("/wallets/", response_class=HTMLResponse)
async def profile(current_user_or_redirect: Annotated[User, Depends(get_current_user)]):
    
    match current_user_or_redirect:
        case UserInDB():
            with open('front/my_wallet.html', 'r') as file:
                data = file.read()
            return HTMLResponse(content=data, status_code=200)
        
        case RedirectResponse():
            return current_user_or_redirect