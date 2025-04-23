from pydantic import BaseModel


class Prompt(BaseModel):
    title: str
    description: str | None
    price: str | None
    statistics: dict | None
    preview: str | None
