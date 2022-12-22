from fastapi import APIRouter, HTTPException, status
from fastapi import Depends
import json

from deps import get_db

from schemas.link import Link, LinkInDB, LinkUpdate
import crud.links as crud
from core.broker import session

router = APIRouter(prefix="/links")


@router.post('/', response_model=LinkInDB)
def post_link(link: Link, db=Depends(get_db)):
    """Метод для создания ссылки в базе данных"""
    result = crud.create_link(db=db, url=link.url)
    session.publish_task(json.dumps(result.as_dict()))
    return LinkInDB(id=result.id, url=result.url, status=result.status)


@router.get('/', response_model=LinkInDB)
def get_link(id: int, db=Depends(get_db)):
    """Метод для получения ссылки из базы данных"""
    result = crud.get_link_by_id(db=db, id=id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return LinkInDB(id=result.id, url=result.url, status=result.status)


@router.put('/', response_model=LinkInDB)
def update_link(link: LinkUpdate, db=Depends(get_db)):
    """Метод для обвновления состояния ссылки"""
    result = crud.update_status_by_id(db=db, id=link.id, status=link.status)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return LinkInDB(id=result.id, url=result.url, status=result.status)

