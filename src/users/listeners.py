from propan_config.router import queue_1, exch, Incoming, call, rabbit_router
from fastapi import Depends
# from fastapi_config.main import app
from propan.fastapi import RabbitRouter
from src.users.pydantic_models import MessageFromChatModel
from src.users.services import save_new_message
from sqlalchemy.orm import Session
# from .main import app
# from main import
from db_config.database import get_db

rabbit_users_listener_router = RabbitRouter("amqp://guest:guest@localhost:5672")


@rabbit_router.broker.handle(queue_1, exch)
async def receive_chat_message(message: str, email: str, photo: str | None, 
                               d = Depends(call), 
                               db: Session = Depends(get_db)):

    message = MessageFromChatModel(message=message,
                                   email=email,
                                   photo=photo)

    await save_new_message(message)
