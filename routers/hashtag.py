from fastapi import Form, Depends, APIRouter
from storages import ClientStorage
from dependencies import get_clients

router = APIRouter(
    prefix='/hashtag',
    tags=["Hashtag"],
    responses={404: {'description': 'Not Found'}}
)

@router.post('/get_top_hashtags')
async def hashtag_top(
        sessionid: str = Form(...),
        name: str = Form(...),
        amount: int = 9,
        clients: ClientStorage = Depends(get_clients),

):
    cl = clients.get(sessionid)
    result = cl.hashtag_medias_top(
        name=name,
        amount=amount)
    return result

@router.post('/get_recent_hashtags')
async def hashtag_recent(
        sessionid: str = Form(...),
        name: str = Form(...),
        amount: int = 9,
        clients: ClientStorage = Depends(get_clients),

):
    cl = clients.get(sessionid)
    result = cl.hashtag_medias_recent(
        name=name,
        amount=amount)
    return result


@router.post('/get_hashtag_info')
def hashtag_info(
        sessionid: str = Form(...),
        name: str = Form(...),
        clients: ClientStorage = Depends(get_clients),


):
    cl = clients.get(sessionid)
    result = cl.hashtag_info(
        name=name,)
    return result
