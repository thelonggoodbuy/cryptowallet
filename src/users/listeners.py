from fastapi import Depends
from propan.fastapi import RabbitRouter
from sqlalchemy.orm import Session
from db_config.database import get_db
from propan_config.router import queue_1, exch, call, rabbit_router

from src.users.schemas import MessageFromChatModel
from src.users.services.services import save_new_message



rabbit_users_listener_router = RabbitRouter("amqp://guest:guest@localhost:5672")


@rabbit_router.broker.handle(queue_1, exch)
async def receive_chat_message(message: str, email: str, photo: str | None, 
                               d = Depends(call), 
                               db: Session = Depends(get_db)):

    message = MessageFromChatModel(message=message,
                                   email=email,
                                   photo=photo)

    await save_new_message(message)