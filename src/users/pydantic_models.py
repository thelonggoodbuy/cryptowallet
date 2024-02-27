
from pydantic import BaseModel
class MessageFromChatModel(BaseModel):

    message: str
    email: str
    photo: bytes | str | None = None