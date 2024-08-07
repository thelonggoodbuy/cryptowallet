from fastapi import Depends, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Annotated
# from src.users.models import User

from src.users.dependencies import get_current_user

from src.users.schemas import User, UserInDB
from src.wallets.services.wallet_etherium_service import WalletEtheriumService
from src.orders.services.commodity_eth_service import CommodityEthService
from src.orders.services.order_eth_service import OrderEthService

from starlette.responses import RedirectResponse


router = APIRouter()


@router.get("/ibay/", response_class=HTMLResponse)
async def render_ibay_html(
    current_user_or_redirect: Annotated[User, Depends(get_current_user)],
):
    match current_user_or_redirect:
        case UserInDB():
            with open("templates/ibay.html", "r") as file:
                data = file.read()
            return HTMLResponse(content=data, status_code=200)

        case RedirectResponse():
            return current_user_or_redirect


@router.get("/wallets-select2/", response_model=dict)
async def get_wallets(
    current_user_or_redirect: Annotated[User, Depends(get_current_user)],
):
    print("=================you want to choose wallet from=======================")
    all_wallets = (
        await WalletEtheriumService.return_wallets_per_user_email_without_sync(
            current_user_or_redirect.email
        )
    )
    print(all_wallets)
    print(len(all_wallets))
    print("======================================================================")
    addresses_dict = [
        {"id": k, "address": "(" + str(v["balance"]) + " ETH" ")" + " " + v["address"]}
        for k, v in all_wallets.items()
    ]
    return JSONResponse(content={"wallets": addresses_dict})


@router.post("/return_all_commodities/")
async def return_all_commodities(
    current_user_or_redirect: Annotated[User, Depends(get_current_user)],
):
    print("--->current_user_or_redirect<---")
    print(current_user_or_redirect)
    print("--------------------------------")
    all_accomodations = await CommodityEthService.return_all_commodities_for_list(
        current_user_or_redirect.id
    )
    return all_accomodations


@router.post("/return_all_orders/")
async def return_all_orders(
    current_user_or_redirect: Annotated[User, Depends(get_current_user)],
):
    print("======current_user_data======")
    print(current_user_or_redirect)
    print("=============================")
    list_users_orders = await OrderEthService.get_all_users_orders_by_user_id(
        current_user_or_redirect.id
    )
    return {"list_users_orders": list_users_orders}
