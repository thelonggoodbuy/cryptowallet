from src.users.repository.message_repository import message_rep_link

from src.users.services.user_service import UserService
from src.users.schemas import MessageFromChatModel
import locale
from propan_config.router import add_to_returning_saved_message_query


locale.setlocale(locale.LC_TIME, "uk_UA")


class MessageService:
    async def return_last_messages():
        messages = await message_rep_link.return_last_10_messages_from_chate()
        # print('-----messages-----')
        # print(messages)
        # print('------------------')
        messages_dict = {}
        for message in messages:
            messages_dict[message.id] = {}
            # print('Id:')
            # print(message.id)
            messages_dict[message.id]["id"] = message.id
            messages_dict[message.id]["message"] = message.text
            messages_dict[message.id]["username"] = message.user.username
            messages_dict[message.id]["date_time"] = message.time_created.strftime(
                "%d %b %H:%M"
            )
            if message.user.photo:
                messages_dict[message.id]["user_photo"] = message.user.photo["url"][1:]
            else:
                messages_dict[message.id]["user_photo"] = None
            if message.photo:
                messages_dict[message.id]["message_photo"] = message.photo["url"][1:]
            else:
                messages_dict[message.id]["message_photo"] = None

        # print('-----messages-----')
        # print(messages_dict)
        # print('------------------')
        return messages_dict

    async def save_new_message(message_from_socket: MessageFromChatModel):
        # print('===save new message data===')
        # print(message_from_socket)
        user = await UserService.return_user_per_email(message_from_socket.email)
        # print('===returned user===')
        # print(user)
        # print(user.username)
        message = await message_rep_link.create_message(message_from_socket, user)
        # print('===returned message===')
        # print(message)
        # print('=========')
        # print(message)
        # print(type(message))
        # print('=========')

        message_dict = {}
        message_dict = {
            "id": message.id,
            "message": message.text,
            "username": user.username,
            "date_time": message.time_created.strftime("%d %b %H:%M"),
        }
        if user.photo:
            message_dict["user_photo"] = user.photo["url"][1:]
        else:
            message_dict["user_photo"] = None
        if message.photo:
            message_dict["message_photo"] = message.photo["url"][1:]

        # print('***')
        # print(message_dict)
        # print('***')

        await add_to_returning_saved_message_query(message_dict)
