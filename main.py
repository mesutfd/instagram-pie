import pkg_resources

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import JSONResponse
from routers import (
    auth, media, video, photo, user,
    igtv, clip, album, story,
    insights, send_direct, hashtag
)
from typing import List, Optional, Dict
from pathlib import Path
import json
from instagrapi import Client
from fastapi import Depends, File, UploadFile, Form
from instagrapi.types import Media, Location, Usertag, UserShort, User, Story

from dependencies import ClientStorage, get_clients


app = FastAPI(prefix = '/instagram/engine/instagrapi')



@app.get("/", tags=["system"], summary="Show Docs")
async def root(request: Request):
    """Redirect to /instagram/engine/instagrapi/docs
    """
    return get_swagger_ui_html(
        openapi_url='/instagram/engine/instagrapi/openapi.json',
        title="API Swagger",
    )

@app.get("/instagram/engine/instagrapi/", tags=["system"], summary="Show Docs")
async def root(request: Request):
    """Redirect to /instagram/engine/instagrapi/docs
    """
    return get_swagger_ui_html(
        openapi_url='./openapi.json',
        title="API Swagger",
    )

@app.get("/instagram/engine/instagrapi", tags=["system"], summary="Show Docs")
async def root(request: Request):
    """Redirect to /instagram/engine/instagrapi/docs
    """
    return get_swagger_ui_html(
        openapi_url='./openapi.json',
        title="API Swagger",
    )

@app.get("/version", tags=["system"], summary="Get dependency versions")
async def version():
    """Get dependency versions
    """
    versions = {}
    for name in ('instagrapi', ):
        item = pkg_resources.require(name)
        if item:
            versions[name] = item[0].version
    return versions

@app.get("/instagram/engine/instagrapi/version", tags=["system"], summary="Get dependency versions")
async def version():
    """Get dependency versions
    """
    versions = {}
    for name in ('instagrapi', ):
        item = pkg_resources.require(name)
        if item:
            versions[name] = item[0].version
    return versions

#Start Routers

#AUTH

@app.post("/auth/login/", tags=["auth"], responses={404: {"description": "Not found"}})
async def auth_login(username: str = Form(...), password: str = Form(...), verification_code: Optional[str] = Form(""), proxy: Optional[str] = Form(""), locale: Optional[str] = Form(""), timezone: Optional[str] = Form(""), clients: ClientStorage = Depends(get_clients)) -> str:
    return await auth.auth_login(username, password, verification_code, proxy, locale, timezone, clients)

@app.post("/auth/relogin", tags=["auth"], responses={404: {"description": "Not found"}})
async def auth_relogin(sessionid: str = Form(...), clients: ClientStorage = Depends(get_clients)) -> str:
    """Relogin by username and password (with clean cookies)
    """
    return await auth.auth_relogin(sessionid, clients)

@app.get("/auth/settings/get", tags=["auth"], responses={404: {"description": "Not found"}})
async def settings_get(sessionid: str, clients: ClientStorage = Depends(get_clients)) -> Dict:
    """Get client's settings
    """
    return await auth.settings_get(sessionid, clients)

@app.post("/auth/settings/set", tags=["auth"], responses={404: {"description": "Not found"}})
async def settings_set(settings: str = Form(...), sessionid: Optional[str] = Form(""), clients: ClientStorage = Depends(get_clients)) -> str:
    """Set client's settings
    """
    return await auth.settings_set(settings, sessionid, clients)

@app.get("/auth/timeline_feed", tags=["auth"], responses={404: {"description": "Not found"}})
async def timeline_feed(sessionid: str, clients: ClientStorage = Depends(get_clients)) -> Dict:
    """Get your timeline feed
    """
    return await auth.timeline_feed(sessionid, clients)

#MEDIA

@app.get("/media/pk_from_code", tags=["media"], responses={404: {"description": "Not found"}})
async def media_pk_from_code(code: str) -> str:
    """Get media pk from code
    """
    return await media.media_pk_from_code(code)

@app.get("/media/pk_from_url", tags=["media"], responses={404: {"description": "Not found"}})
async def media_pk_from_url(url: str) -> str:
    """Get Media PK from URL
    """
    return await media.media_pk_from_url(url)

@app.post("/media/info", response_model=Media, tags=["media"], responses={404: {"description": "Not found"}})
async def media_info(sessionid: str = Form(...), pk: int = Form(...), use_cache: Optional[bool] = Form(True), clients: ClientStorage = Depends(get_clients)) -> Media:
    """Get media info by pk
    """
    return await media.media_info(sessionid, pk, use_cache, clients)

@app.post("/media/user_medias", response_model=List[Media], tags=["media"], responses={404: {"description": "Not found"}})
async def user_medias(sessionid: str = Form(...), user_id: int = Form(...), amount: Optional[int] = Form(50), clients: ClientStorage = Depends(get_clients)) -> List[Media]:
    """Get a user's media
    """
    return await media.user_medias(sessionid, user_id, amount, clients)

@app.post("/media/likers", response_model=List[UserShort], tags=["media"], responses={404: {"description": "Not found"}})
async def media_likers(sessionid: str = Form(...), media_id: str = Form(...), clients: ClientStorage = Depends(get_clients)) -> List[UserShort]:
    """Get user's likers
    """
    return await media.media_likers(sessionid, media_id, clients)

#USER

@app.post("/user/followers", response_model=Dict[int, UserShort], tags=["user"], responses={404: {"description": "Not found"}})
async def user_followers(sessionid: str = Form(...), user_id: str = Form(...), use_cache: Optional[bool] = Form(True), amount: Optional[int] = Form(0), clients: ClientStorage = Depends(get_clients)) -> Dict[int, UserShort]:
    """Get user's followers
    """
    return await user.user_followers(sessionid, user_id, use_cache, amount, clients)

@app.post("/user/following", response_model=Dict[int, UserShort], tags=["user"], responses={404: {"description": "Not found"}})
async def user_following(sessionid: str = Form(...), user_id: str = Form(...), use_cache: Optional[bool] = Form(True), amount: Optional[int] = Form(0), clients: ClientStorage = Depends(get_clients)) -> Dict[int, UserShort]:
    """Get user's followers information
    """
    return await user.user_following(sessionid, user_id, use_cache, amount, clients)

@app.post("/user/info", response_model=User, tags=["user"], responses={404: {"description": "Not found"}})
async def user_info(sessionid: str = Form(...), user_id: str = Form(...), use_cache: Optional[bool] = Form(True), clients: ClientStorage = Depends(get_clients)) -> User:
    """Get user object from user id
    """
    return await user.user_info(sessionid, user_id, use_cache, clients)

@app.post("/user/info_by_username", response_model=User, tags=["user"], responses={404: {"description": "Not found"}})
async def user_info_by_username(sessionid: str = Form(...), username: str = Form(...), use_cache: Optional[bool] = Form(True), clients: ClientStorage = Depends(get_clients)) -> User:
    """Get user object from username
    """
    return await user.user_info_by_username(sessionid, username, use_cache, clients)

@app.post("/user/id_from_username", response_model=int, tags=["user"], responses={404: {"description": "Not found"}})
async def user_id_from_username(sessionid: str = Form(...), username: str = Form(...), clients: ClientStorage = Depends(get_clients)) -> int:
    """Get user id from username
    """
    return await user.user_id_from_username(sessionid, username, clients)

@app.post("/user/username_from_id", response_model=str, tags=["user"], responses={404: {"description": "Not found"}})
async def username_from_user_id(sessionid: str = Form(...), user_id: int = Form(...), clients: ClientStorage = Depends(get_clients)) -> str:
    """Get username from user id
    """
    return await user.username_from_user_id(sessionid, user_id, clients)

#STORY

@app.post("/story/user_stories", response_model=List[Story], tags=["story"], responses={404: {"description": "Not found"}})
async def story_user_stories(sessionid: str = Form(...), user_id: str = Form(...), amount: Optional[int] = Form(None), clients: ClientStorage = Depends(get_clients)) -> List[Story]:
    """Get a user's stories
    """
    return await story.story_user_stories(sessionid, user_id, amount, clients)

@app.post("/story/info", response_model=Story, tags=["story"], responses={404: {"description": "Not found"}})
async def story_info(sessionid: str = Form(...), story_pk: int = Form(...), use_cache: Optional[bool] = Form(True), clients: ClientStorage = Depends(get_clients)) -> Story:
    """Get Story by pk or id
    """
    return await story.story_info(sessionid, story_pk, use_cache, clients)

#DIRECT

@app.post('/direct/send_by_username', tags=["direct"], responses={404: {"description": "Not found"}})
async def send_direct_message_by_username(sessionid: str = Form(...), target_username: str = Form(...), message_body: str = Form(...), clients: ClientStorage = Depends(get_clients)):
    return await send_direct.send_direct_message_by_username(sessionid, target_username, message_body, clients)

@app.post('/direct/send_by_id', tags=["direct"], responses={404: {"description": "Not found"}})
async def send_direct_message_by_id(sessionid: str = Form(...), target_userid: int = Form(...), message_body: str = Form(...), clients: ClientStorage = Depends(get_clients),):
    return await send_direct.send_direct_message_by_id(sessionid, target_userid, message_body, clients)

@app.post('/direct/send_photo_by_id', tags=["direct"], responses={404: {"description": "Not found"}})
async def send_direct_photo_by_id(sessionid: str = Form(...), path: Path = Form(...), user_id: list[int] = Form(...), clients: ClientStorage = Depends(get_clients)):
    return await send_direct.send_direct_photo_by_id(sessionid, path, user_id, clients)

@app.post('/direct/send_photo_by_username', tags=["direct"], responses={404: {"description": "Not found"}})
async def send_direct_photo_by_username(sessionid: str = Form(...), path: Path = Form(...), username: list[int] = Form(...), clients: ClientStorage = Depends(get_clients)):
    return await send_direct.send_direct_photo_by_username(sessionid, path, username, clients)

#HASHTAG

@app.post('/hashtag/get_top_hashtags', tags=["hashtag"], responses={404: {"description": "Not found"}})
async def hashtag_top(sessionid: str = Form(...), name: str = Form(...), amount: int = Form(9), clients: ClientStorage = Depends(get_clients)):
    return await hashtag.hashtag_top(sessionid, name, amount, clients)

@app.post('/hashtag/get_recent_hashtags', tags=["hashtag"], responses={404: {"description": "Not found"}})
async def hashtag_recent(sessionid: str = Form(...), name: str = Form(...), amount: int = Form(9), clients: ClientStorage = Depends(get_clients)):
    return await hashtag.hashtag_recent(sessionid, name, amount, clients)

@app.post('/hashtag/get_hashtag_info', tags=["hashtag"], responses={404: {"description": "Not found"}})
async def hashtag_info(sessionid: str = Form(...), name: str = Form(...), clients: ClientStorage = Depends(get_clients)):
    return await hashtag.hashtag_info(sessionid, name, clients)





#End Routers

@app.exception_handler(Exception)
async def handle_exception(request, exc: Exception):
    return JSONResponse({
        "detail": str(exc),
        "exc_type": str(type(exc).__name__)
    }, status_code=500)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    # for route in app.routes:
    #     body_field = getattr(route, 'body_field', None)
    #     if body_field:
    #         body_field.type_.__name__ = 'name'
    openapi_schema = get_openapi(
        title="NAJI Instagrapi API",
        version="1.0.0",
        description="RESTful API Service for Instagram OSINT",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
