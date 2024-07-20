from pydantic import BaseModel




class NewBlochainSchema(BaseModel):
    blockchain_type: str
    title: str
    photo: bytes | str | None = None


class NewAssetSchema(BaseModel):
    type: str
    text: str
    decimal_places: int
    title: str
    code: str