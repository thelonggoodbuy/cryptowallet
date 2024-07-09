from sqladmin import ModelView
from src.users.models import User, Message
from src.wallets.models import Wallet, Asset, Blockchain
from src.orders.models import Commodity, Order
from src.etherium.models import Transaction
import wtforms
from wtforms_sqlalchemy.fields import QuerySelectField
from db_config.database import async_session
from sqladmin.ajax import create_ajax_loader
from wtforms.widgets import TextArea
from wtforms import TextAreaField
from sqlalchemy import Select
import asyncio
from asgiref.sync import async_to_sync, sync_to_async
from fastapi import Request
from sqlalchemy.orm import contains_eager
from sqlalchemy.ext.asyncio import async_sessionmaker
from db_config.database import engine
from sqlalchemy import select
from sqlalchemy import desc
from db_config.database import async_session
from src.users.services.user_service import UserService
from markupsafe import Markup
from sqlalchemy.orm import joinedload
from jose import jwt



class ModelViewWithCustomTemplates(ModelView):
    list_template = 'list.html'
    create_template = 'create.html'
    details_template = 'details.html'
    edit_template = 'edit.html'



class UserAdmin(ModelViewWithCustomTemplates, model=User):

    column_list = [User.id, User.email]
    column_details_exclude_list = [User.messages, User.password]
    form_excluded_columns = [User.messages, User.password]




class MessageAdmin(ModelViewWithCustomTemplates, model=Message):
    # list page
    column_list = ['user.email', Message.text, Message.time_created]
    column_formatters = {Message.text: lambda m, a: m.text[:5] + ' ...' if len(m.text)>5 else m.text,
                         Message.time_created: lambda m, a: m.time_created.strftime("%d.%m.%Y, %H:%M:%S")}
    column_searchable_list = ['user.email']
    column_sortable_list = ['user.email', Message.time_created]
    column_default_sort = [(Message.time_created, True), ]
    page_size = 20
    # detail page
    column_formatters_detail = {Message.time_created: lambda m, a: m.time_created.strftime("%d.%m.%Y, %H:%M:%S"),
                                Message.user: lambda message_object, user: f'Користувач №{message_object.user.id} з email {message_object.user.email}'}
    # total properties
    column_labels = {"user.email": "Email користувача",
                     Message.text: "Текст повідомлення",
                     Message.time_created: "Час створення",
                     Message.photo: "Фото користувача",
                     "user": "Користувач"}


    form_columns = ['user', 'text', 'photo', 'time_created']



    form_args = {
        'text': {'label': 'Текст повідомлення', 'widget': TextArea()},
        'photo': {'label': 'Фото користувача'},
        'user': {
            'label': 'Відправник',
        }
    }

    form_widget_args = {
        'text': {'rows': 10, 'cols': 50},
        'photo': {'rows': 5, 'cols': 50}
    }

    form_overrides = {
        'text': TextAreaField,
        # 'user': QuerySelectField
    }



# admin views
class WalletAdmin(ModelViewWithCustomTemplates, model=Wallet):
    column_list = [Wallet.id,
                   Wallet.address,
                   Wallet.user,
                   Wallet.balance,
                   Wallet.asset]
    column_details_exclude_list = ['id', 'private_key', 'asset_id']

    # form_columns = ['user', 'commodity']

    # form_widget_args = {
    #     'commodity': {'readonly': True},
    # }
    # form_columns = ['user', 'text', 'photo', 'time_created']

    form_excluded_columns = ['private_key', 'commodity']



class OrderAdmin(ModelViewWithCustomTemplates, model=Order):
    column_list = [Order.commodity,
                   Order.transaction,
                   Order.return_transaction,
                   Order.order_status,
                   Order.date_time_transaction]

    column_details_exclude_list = ['id', 'commodity_id', 'transaction_id', 'return_transaction_id']


class CommodityAdmin(ModelViewWithCustomTemplates, model=Commodity):
    column_list = [Commodity.title,
                   Commodity.wallet,
                   Commodity.price]
    column_details_exclude_list = ['id', 'wallet_id']


class TransactionAdmin(ModelViewWithCustomTemplates, model=Transaction):
    column_list = [Transaction.txn_hash,
                   Transaction.value,
                   Transaction.txn_fee,
                   Transaction.status]




from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from src.users.services.user_service import UserService
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

# SECRET_KEY = "e902bbf3a6c28106f91028b01e6158bcab2360acc0676243d70404fe6e731b58"
# ALGORITHM = "HS256"



class AdminAuth(AuthenticationBackend):

    async def authenticate(self, request: Request) -> bool:
        access_token = request.cookies.get('access_token')
        is_admin_status = await UserService.check_if_user_is_admin_by_token(access_token)
        if is_admin_status == True:
            return True
        else:
            # return RedirectResponse(url="http://127.0.0.1:8000/users/profile/")
            return RedirectResponse(url=request.url_for('user_profile'))


authentication_backend = AdminAuth(secret_key="TestAdminSecretKey")
