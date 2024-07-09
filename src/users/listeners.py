from fastapi import Depends
from propan.fastapi import RabbitRouter
from propan_config.router import queue_1, exch, call, rabbit_router
import os

from src.users.schemas import MessageFromChatModel

# from src.users.services.services import save_new_message
from src.users.services.message_service import MessageService

RABBIT_ADDRESS = os.environ.get('RABBIT_ADDRESS')
rabbit_users_listener_router = RabbitRouter(RABBIT_ADDRESS)


@rabbit_router.broker.handle(queue_1, exch)
async def receive_chat_message(
    message: str, email: str, photo: str | None, d=Depends(call)
):
    message = MessageFromChatModel(message=message, email=email, photo=photo)

    await MessageService.save_new_message(message)
