from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from typing import Annotated, Optional
from src.users.models import User
from fastapi import Depends
from src.users.routers import get_current_user, UserInDB
from starlette.responses import RedirectResponse
from typing import Union



router = APIRouter()


@router.get("/wallets/", response_class=HTMLResponse)
async def profile(current_user_or_redirect: Annotated[User, Depends(get_current_user)]):
    """
    Endpoint for returning the "my_wallet.html" template
    and validating user access using a token received from the front-end.

    Args:
        current_user_or_redirect (Annotated[User, Depends(get_current_user)]):
            Dependency injection result that validates user access.
            It returns a User object if valid, or a RedirectResponse
            object to redirect to the login page if unauthorized.

    Returns:
        Optional[HTMLResponse]: Object containing the rendered template or
                      a RedirectResponse object (if unauthorized)
                      which redirect to login page.
    """
    match current_user_or_redirect:   
        case UserInDB():
            with open('front/my_wallet.html', 'r') as file:
                data = file.read()
            return HTMLResponse(content=data, status_code=200)
        
        case RedirectResponse():
            print('3')
            return current_user_or_redirect