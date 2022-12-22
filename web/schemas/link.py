from typing import Optional

from pydantic import BaseModel


class Link(BaseModel):
    url: str


class LinkUpdate(BaseModel):
    id: int
    status: str


class LinkInDB(Link):
    id: int
    status: Optional[str]

    class Config:
        orm_mode = True
