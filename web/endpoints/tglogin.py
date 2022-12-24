import hmac
from hashlib import sha256
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from fastapi import Depends
from fastapi.responses import RedirectResponse
import json

from deps import get_db
from pydantic import Field

from schemas.link import Link, LinkInDB, LinkUpdate
import crud.links as crud
from core.broker import session

router = APIRouter(prefix="/tglogin")

BOT_TOKEN = '5787993542:AAETVt3Zk88jim0GAEWJJkSLirvrzz9n1MI'


# @router.post('/', response_model=LinkInDB)
# def post_link(link: Link, db=Depends(get_db)):
#     """Метод для создания ссылки в базе данных"""
#     result = crud.create_link(db=db, url=link.url)
#     session.publish_task(json.dumps(result.as_dict()))
#     return LinkInDB(id=result.id, url=result.url, result_url=result.result_url)


@router.get('/')
def get_link(id: int, first_name: str, auth_date: int, hash: str, username: Optional[str] = Query(None), photo_url: Optional[str] = Query(None), db=Depends(get_db)):
    """Метод для авторизации через тг"""
    fields = dict({"id": id, "first_name": first_name, 'username': username, 'photo_url': photo_url, 'auth_date': auth_date, 'hash': hash})
    hash = fields.pop('hash')
    auth_date = fields.get('auth_date')
    id = fields.get('id')
    fields = dict(sorted(fields.items(), key=lambda item: item[0]))
    data_check_string = ('\n'.join('='.join((key, str(val))) for (key, val) in fields.items()))
    secret = sha256(BOT_TOKEN.encode('utf-8'))
    sig = hmac.new(secret.digest(), data_check_string.encode('utf-8'), sha256).hexdigest()
    if sig == hash:
        response = RedirectResponse('/')
        response.set_cookie(key="token", value=hash)
        response.set_cookie(key="tg_uid", value=id)
        response.set_cookie(key="tg_uname", value=username)
        return response
    return "Error while logging in"
    # result = crud.get_link_by_id(db=db, id=id)
    # if result is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # return LinkInDB(id=result.id, url=result.url, result_url=result.result_url)


# @router.put('/', response_model=LinkInDB)
# def update_link(link: LinkUpdate, db=Depends(get_db)):
#     """Метод для обвновления состояния ссылки"""
#     result = crud.update_result_url_by_id(db=db, id=link.id, result_url=link.result_url)
#     if result is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
#     return LinkInDB(id=result.id, url=result.url, result_url=result.result_url)

