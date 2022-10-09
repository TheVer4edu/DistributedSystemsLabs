from fastapi import APIRouter, HTTPException, status
from fastapi import Depends

from deps import get_db

from schemas.link import Link, LinkInDB
import crud.links as crud

router = APIRouter(prefix="/links")


@router.post('/', response_model=LinkInDB)
def post_link(link: Link, db=Depends(get_db)):
    """Метод для создания ссылки в базе данных"""
    result = crud.create_link(db=db, url=link.url)
    return LinkInDB(id=result.id, url=result.url)


@router.get('/', response_model=LinkInDB)
def get_link(id: int, db=Depends(get_db)):
    """Метод для получения ссылки из базы данных"""
    result = crud.get_link_by_id(db=db, id=id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return LinkInDB(id=result.id, url=result.url)
