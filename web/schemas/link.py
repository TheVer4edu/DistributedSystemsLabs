from pydantic import BaseModel


class Link(BaseModel):
    url: str


class LinkInDB(Link):
    id: int

    class Config:
        orm_mode = True
