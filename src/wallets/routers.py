from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from typing import Annotated
from src.users.models import User
from fastapi import Depends
from src.users.routers import get_current_user, UserInDB
from starlette.responses import RedirectResponse
from typing import List
from fastapi.responses import JSONResponse
from src.etherium.services.transaction_eth_service import TransactionETHService

from pydantic import BaseModel

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
            with open("front/my_wallet.html", "r") as file:
                data = file.read()
            return HTMLResponse(content=data, status_code=200)

        case RedirectResponse():
            print("3")
            return current_user_or_redirect


# Sample data
data = [
    {
        "id": 73,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    {
        "id": 74,
        "txn_hash": "0xa02811111b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA77705e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f88848b83Ab3940A7f41204C3c5Ab1",
        "age": "7 sec",
        "txn_fee": "0.033312",
        "status": "success",
    },
    {
        "id": 77,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    {
        "id": 80,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    {
        "id": 91,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    {
        "id": 108,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    {
        "id": 116,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    {
        "id": 120,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    {
        "id": 124,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    {
        "id": 129,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    {
        "id": 132,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    {
        "id": 138,
        "txn_hash": "0xa02885d3b8376ae8244db41599f424215c9f726a1504b1dad9680a045d691b75",
        "from": "0x7B8A304CA89E005e62cF093C3a7E36f295Dc4569",
        "to": "0x5ee1F7982f93D448b83Ab3940A7f41204C3c5Ab1",
        "age": "5 sec",
        "txn_fee": "0.0012312",
        "status": "success",
    },
    # Add more sample data as needed
]


# class Order(BaseModel):
#     column: int
#     dir: str


class DataTablesRequest(BaseModel):
    draw: int
    start: int = Query(0)
    length: int = Query(10)
    # search: Dict[str, Any]
    # order: List[Dict[str, Any]]
    # columns: List[Dict[str, Any]]


# def sort_data(data, order):
#     if not order:
#         return data

#     for o in order:
#         column_idx = o.column
#         column_name = ["id", "name", "age"][column_idx]  # Mapping column index to name
#         reverse = (o.dir == "desc")
#         data.sort(key=lambda x: x[column_name], reverse=reverse)

#     return data


# @router.get("/get_transactions_from_concrete_wallet/{wallet_id}")
# async def get_transaction_from_concrete_wallet(wallet_id: int,
#                                             draw: int,
#                                             start: int = Query(0),
#                                             length: int = Query(10)):

#     paginated_data = data[start:start + length]

#     response_dict = {
#         "draw": draw,
#         "recordsTotal": len(data),
#         "recordsFiltered": len(data),
#         "data": paginated_data,
#     }

#     return response_dict


class Order(BaseModel):
    column: int
    dir: str


class DataTableParams(BaseModel):
    draw: int = 1
    start: int = 0
    length: int = 10
    order: List[Order]


class DataTableParamsForService(BaseModel):
    wallet_id: int
    draw: int
    start: int
    length: int
    order_column: int
    order_dir: str


# TODO add schema and comments
@router.get("/get_transactions_from_concrete_wallet/{wallet_id}")
async def get_transaction_from_concrete_wallet(request: Request):
    # Retrieve query parameters for sorting
    wallet_id = int(request.query_params.get("wallet_id", 1))
    draw = int(request.query_params.get("draw", 1))
    start = int(request.query_params.get("start", 0))
    length = int(request.query_params.get("length", 10))
    order_column = int(request.query_params.get("order[0][column]", 0))
    order_dir = request.query_params.get("order[0][dir]", "asc")
    # forming datatable object with all needfull parameters
    data_table_obj = DataTableParamsForService(
        wallet_id=wallet_id,
        draw=draw,
        start=start,
        length=length,
        order_column=order_column,
        order_dir=order_dir,
    )

    dt_response = await TransactionETHService.return_all_transactions_in_ssp_datatable(
        data_table_obj
    )
    total_records = dt_response["total_transactions_counter"]
    records_filtered = len(dt_response["result_list"])

    response = {
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": total_records,
        "data": dt_response["result_list"],
    }

    return JSONResponse(response)


# @router.get("/get_transactions_from_concrete_wallet/{wallet_id}")
# async def get_transaction_from_concrete_wallet(
#     draw: int,
#     start: int = Query(0),
#     length: int = Query(10)
# ) -> Dict[str, Any]:
#     # Pagination
#     paginated_data = data[start:start + length]

#     return {
#         "draw": draw,
#         "recordsTotal": len(data),
#         "recordsFiltered": len(data),
#         "data": paginated_data,
#     }
