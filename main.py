import json
import random
from pathlib import Path
from typing import List, Optional, Dict

import pkg_resources
from fastapi import Depends, Form
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from instagrapi import Client
from instagrapi.types import Media, UserShort, User, Story
from starlette.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from dependencies import ClientStorage, get_clients

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["system"], summary="Show Docs")
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
    for name in ('instagrapi',):
        item = pkg_resources.require(name)
        if item:
            versions[name] = item[0].version
    return versions


# Start Routers

# AUTH

@app.post("/auth/login", tags=["auth"], responses={404: {"description": "Not found"}})
async def auth_login(username: str = Form(...), password: str = Form(...), verification_code: Optional[str] = Form(""),
                     proxy: Optional[str] = Form(""), locale: Optional[str] = Form(""),
                     timezone: Optional[str] = Form(""), clients: ClientStorage = Depends(get_clients)) -> str:
    """Login by username and password with 2FA
    """
    cl = clients.client()
    if proxy != "":
        cl.set_proxy(proxy)

    if locale != "":
        cl.set_locale(locale)

    if timezone != "":
        cl.set_timezone_offset(timezone)

    result = cl.login(
        username,
        password,
        verification_code=verification_code
    )
    if result:
        clients.set(cl)
        return cl.sessionid
    return result


@app.post("/auth/relogin", tags=["auth"], responses={404: {"description": "Not found"}})
async def auth_relogin(sessionid: str = Form(...), proxy: str = Form(...),
                       clients: ClientStorage = Depends(get_clients)) -> bool:
    """Relogin by username and password (with clean cookies)
    """
    cl = clients.get(sessionid, proxy)
    result = cl.relogin()
    return result


@app.get("/auth/settings/get", tags=["auth"], responses={404: {"description": "Not found"}})
async def settings_get(sessionid: str, proxy: str, clients: ClientStorage = Depends(get_clients)) -> str:
    """Get client's settings
    """
    cl = clients.get(sessionid, proxy)
    return str(cl.get_settings())


# @app.post("/auth/settings/set", tags=["auth"], responses={404: {"description": "Not found"}})
# async def settings_set(settings: str = Form(...), sessionid: Optional[str] = Form(""),
#                        clients: ClientStorage = Depends(get_clients)) -> str:
#     """Set client's settings
#     """
#     if sessionid != "":
#         cl = clients.get(sessionid)
#     else:
#         cl = clients.client()
#     cl.set_settings(json.loads(settings))
#     cl.expose()
#     clients.set(cl)
#     return cl.sessionid


# @app.get("/auth/timeline_feed", tags=["auth"], responses={404: {"description": "Not found"}})
# async def timeline_feed(sessionid: str, clients: ClientStorage = Depends(get_clients)) -> Dict:
#     """Get your timeline feed
#     """
#     cl = clients.get(sessionid)
#     return cl.get_timeline_feed()


# MEDIA

@app.get("/media/pk_from_code", tags=["media"], responses={404: {"description": "Not found"}})
async def media_pk_from_code(code: str = Form(...), proxy: str = Form(...)) -> str:
    """Get media pk from code
    """
    return str(Client(proxy=proxy).media_pk_from_code(code))


@app.get("/media/pk_from_url", tags=["media"], responses={404: {"description": "Not found"}})
async def media_pk_from_url(url: str = Form(...), proxy: str = Form(...)) -> str:
    """Get Media PK from URL
    """
    return str(Client(proxy=proxy).media_pk_from_url(url))


@app.post("/media/info", response_model=Media, tags=["media"], responses={404: {"description": "Not found"}})
async def media_info(sessionid: str = Form(...), pk: int = Form(...), proxy: str = Form(...),
                     use_cache: Optional[bool] = Form(True),
                     clients: ClientStorage = Depends(get_clients)) -> Media:
    """Get media info by pk
    """
    cl = clients.get(sessionid, proxy)
    return cl.media_info(pk, use_cache)


@app.post("/media/user_medias", response_model=List[Media], tags=["media"],
          responses={404: {"description": "Not found"}})
async def user_medias(sessionid: str = Form(...), user_id: int = Form(...), amount: Optional[int] = Form(50),
                      proxy: str = Form(...),
                      clients: ClientStorage = Depends(get_clients)) -> List[Media]:
    """Get a user's media
    """
    cl = clients.get(sessionid, proxy)
    return cl.user_medias(user_id, amount)


@app.post("/media/likers", response_model=List[UserShort], tags=["media"],
          responses={404: {"description": "Not found"}})
async def media_likers(sessionid: str = Form(...), media_id: str = Form(...), proxy: str = Form(...),
                       clients: ClientStorage = Depends(get_clients)) -> List[UserShort]:
    """Get user's likers
    """
    cl = clients.get(sessionid, proxy)
    return cl.media_likers(media_id)


@app.post('/media/comments', tags=["media"], responses={404: {"description": "Not found"}})
async def get_comments(sessionid: str = Form(...), media_id: str = Form(...), amount: int = Form(30),
                       proxy: str = Form(...),
                       clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    return cl.media_comments(media_id, amount)


@app.post("/media/tagged_post_by_id", tags=["media"], responses={404: {"description": "Not found"}})
async def get_tagged_posts_by_user_id(
        sessionid: str = Form(...),
        userid: int = Form(...),
        amount: int = Form(...),
        proxy: str = Form(...),
        sleep: Optional[int] = Form(2),
        clients: ClientStorage = Depends(get_clients)) -> List[UserShort]:
    cl = clients.get(sessionid, proxy)

    posts = cl.usertag_medias_gql(userid, amount, sleep)

    return posts


@app.post("/media/tagged_post_by_username", tags=["media"], responses={404: {"description": "Not found"}})
async def get_tagged_posts_by_user_name(
        sessionid: str = Form(...),
        username: str = Form(...),
        amount: int = Form(...),
        proxy: str = Form(...),
        sleep: Optional[int] = Form(2),
        clients: ClientStorage = Depends(get_clients)) -> List[UserShort]:
    cl = clients.get(sessionid, proxy)

    user_id = int(cl.user_id_from_username(username))
    posts = cl.usertag_medias_gql(user_id, amount, sleep)

    return posts


# USER

@app.post("/user/followers", response_model=Dict[int, UserShort], tags=["user"],
          responses={404: {"description": "Not found"}})
async def user_followers(sessionid: str = Form(...), user_id: str = Form(...), use_cache: Optional[bool] = Form(True),
                         proxy: str = Form(...),
                         amount: Optional[int] = Form(12), clients: ClientStorage = Depends(get_clients)) -> Dict[
    int, UserShort]:
    """Get user's followers
    """
    cl = clients.get(sessionid, proxy)
    return cl.user_followers(user_id, use_cache, amount)


@app.post("/user/following", response_model=Dict[int, UserShort], tags=["user"],
          responses={404: {"description": "Not found"}})
async def user_following(sessionid: str = Form(...), user_id: str = Form(...), use_cache: Optional[bool] = Form(True),
                         proxy: str = Form(...),
                         amount: Optional[int] = Form(0), clients: ClientStorage = Depends(get_clients)) -> Dict[
    int, UserShort]:
    """Get user's followers information
    """
    cl = clients.get(sessionid, proxy)
    return cl.user_following(user_id, use_cache, amount)


@app.post("/user/info", response_model=User, tags=["user"], responses={404: {"description": "Not found"}})
async def user_info(sessionid: str = Form(...), user_id: str = Form(...), use_cache: Optional[bool] = Form(True),
                    proxy: str = Form(...),
                    clients: ClientStorage = Depends(get_clients)) -> User:
    """Get user object from user id
    """
    cl = clients.get(sessionid, proxy)
    return cl.user_info(user_id, use_cache)


@app.post("/user/info_by_username", response_model=User, tags=["user"], responses={404: {"description": "Not found"}})
async def user_info_by_username(sessionid: str = Form(...), username: str = Form(...),
                                proxy: str = Form(...),
                                use_cache: Optional[bool] = Form(True),
                                clients: ClientStorage = Depends(get_clients)) -> User:
    """Get user object from username
    """
    cl = clients.get(sessionid, proxy)
    return cl.user_info_by_username(username, use_cache)


@app.post("/user/id_from_username", response_model=int, tags=["user"], responses={404: {"description": "Not found"}})
async def user_id_from_username(sessionid: str = Form(...), username: str = Form(...), proxy: str = Form(...),
                                clients: ClientStorage = Depends(get_clients)) -> int:
    """Get user id from username
    """
    cl = clients.get(sessionid, proxy)
    return cl.user_id_from_username(username)


@app.post("/user/username_from_id", response_model=str, tags=["user"], responses={404: {"description": "Not found"}})
async def username_from_user_id(sessionid: str = Form(...), user_id: int = Form(...), proxy: str = Form(...),
                                clients: ClientStorage = Depends(get_clients)) -> str:
    """Get username from user id
    """
    cl = clients.get(sessionid, proxy)
    return cl.username_from_user_id(user_id)


@app.post('/user/search_follower', tags=["user"], responses={404: {"description": "Not found"}})
async def search_followers(sessionid: str = Form(...), user_id: int = Form(...), query: str = Form(...),
                           proxy: str = Form(...),
                           clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    return cl.search_followers(user_id, query)


@app.post('/user/search_following', tags=["user"], responses={404: {"description": "Not found"}})
async def search_followings(sessionid: str = Form(...), user_id: int = Form(...), query: str = Form(...),
                            proxy: str = Form(...),
                            clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    return cl.search_following(user_id, query)


# STORY
@app.post("/story/user_stories", response_model=List[Story], tags=["story"],
          responses={404: {"description": "Not found"}})
async def story_user_stories(sessionid: str = Form(...), user_id: str = Form(...), amount: Optional[int] = Form(None),
                             proxy: str = Form(...),
                             clients: ClientStorage = Depends(get_clients)) -> List[Story]:
    """Get a user's stories
    """
    cl = clients.get(sessionid, proxy)
    return cl.user_stories(user_id, amount)


@app.post("/story/info", response_model=Story, tags=["story"], responses={404: {"description": "Not found"}})
async def story_info(sessionid: str = Form(...), story_pk: int = Form(...), use_cache: Optional[bool] = Form(True),
                     proxy: str = Form(...),
                     clients: ClientStorage = Depends(get_clients)) -> Story:
    """Get Story by pk or id
    """
    cl = clients.get(sessionid, proxy)
    return cl.story_info(story_pk, use_cache)


# Download


@app.post("/download/download_story_by_url", tags=["Download"], responses={404: {"description": "Not found"}})
async def story_download_by_url(sessionid: str = Form(...),
                                url: str = Form(...),
                                filename: Optional[str] = Form(""),
                                folder: Optional[Path] = Form(""),
                                proxy: str = Form(...),
                                returnFile: Optional[bool] = Form(True),
                                clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.story_download_by_url(url, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@app.post("/download/download_story_by_pk", tags=["Download"], responses={404: {"description": "Not found"}})
async def story_download(sessionid: str = Form(...),
                         story_pk: int = Form(...),
                         filename: Optional[str] = Form(""),
                         folder: Optional[Path] = Form(""),
                         proxy: str = Form(...),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.story_download(story_pk, filename, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@app.post("/download/download_photo_by_pk", tags=["Download"], responses={404: {"description": "Not found"}})
async def photo_download(sessionid: str = Form(...),
                         media_pk: int = Form(...),
                         folder: Optional[Path] = Form(""),
                         proxy: str = Form(...),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.photo_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@app.post("/download/download_photo_by_url", tags=["Download"], responses={404: {"description": "Not found"}})
async def photo_download_by_urll(sessionid: str = Form(...),
                                 media_pk: int = Form(...),
                                 filename: Optional[str] = Form(""),
                                 proxy: str = Form(...),
                                 returnFile: Optional[bool] = Form(True),
                                 clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.photo_download_by_url(media_pk, filename)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@app.post("/download/download_video_by_pk", tags=["Download"], responses={404: {"description": "Not found"}})
async def video_download(sessionid: str = Form(...),
                         media_pk: int = Form(...),
                         folder: Optional[Path] = Form(""),
                         proxy: str = Form(...),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.video_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@app.post("/download/download_video_by_url", tags=["Download"], responses={404: {"description": "Not found"}})
async def video_download_by_urll(sessionid: str = Form(...),
                                 media_pk: int = Form(...),
                                 filename: Optional[str] = Form(""),
                                 proxy: str = Form(...),
                                 returnFile: Optional[bool] = Form(True),
                                 clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.video_download_by_url(media_pk, filename)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@app.post("/download/download_album_by_pk", tags=["Download"], responses={404: {"description": "Not found"}})
async def album_download(sessionid: str = Form(...),
                         media_pk: int = Form(...),
                         folder: Optional[Path] = Form(""),
                         proxy: str = Form(...),
                         clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.album_download(media_pk, folder)
    return result


@app.post("/download/download_album_by_url", tags=["Download"], responses={404: {"description": "Not found"}})
async def album_download_by_urll(sessionid: str = Form(...),
                                 media_pk: int = Form(...),
                                 filename: Optional[str] = Form(""),
                                 proxy: str = Form(...),
                                 clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.album_download_by_urls(media_pk, filename)
    return result


@app.post("/download/download_igtv_by_pk", tags=["Download"], responses={404: {"description": "Not found"}})
async def igtv_download(sessionid: str = Form(...),
                        media_pk: int = Form(...),
                        folder: Optional[Path] = Form(""),
                        proxy: str = Form(...),
                        returnFile: Optional[bool] = Form(True),
                        clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.igtv_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@app.post("/download/download_igtv_by_url", tags=["Download"], responses={404: {"description": "Not found"}})
async def igtv_download_by_urll(sessionid: str = Form(...),
                                media_pk: int = Form(...),
                                filename: Optional[str] = Form(""),
                                proxy: str = Form(...),
                                returnFile: Optional[bool] = Form(True),
                                clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.igtv_download_by_url(media_pk, filename)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@app.post("/download/download_clip_by_pk", tags=["Download"], summary='for download reels',
          responses={404: {"description": "Not found"}})
async def clip_download(sessionid: str = Form(...),
                        media_pk: int = Form(...),
                        folder: Optional[Path] = Form(""),
                        proxy: str = Form(...),
                        returnFile: Optional[bool] = Form(True),
                        clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.clip_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result


@app.post("/download/download_clip_by_url", tags=["Download"], summary='for download reels',
          responses={404: {"description": "Not found"}})
async def clip_download_by_urll(sessionid: str = Form(...),
                                media_pk: int = Form(...),
                                filename: Optional[str] = Form(""),
                                proxy: str = Form(...),
                                returnFile: Optional[bool] = Form(True),
                                clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.clip_download_by_url(media_pk, filename)
    if returnFile:
        return FileResponse(result)
    else:
        return result


# DIRECT

@app.post('/direct/send_by_username', tags=["direct"], responses={404: {"description": "Not found"}})
async def send_direct_message_by_username(sessionid: str = Form(...), target_username: str = Form(...),
                                          proxy: str = Form(...),
                                          message_body: str = Form(...), clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    taken_username = cl.user_id_from_username(target_username)
    taken_user_id = int(taken_username)
    result = cl.direct_send(f"{message_body}", [taken_user_id, ])
    return result


@app.post('/direct/send_by_id', tags=["direct"], responses={404: {"description": "Not found"}})
async def send_direct_message_by_id(sessionid: str = Form(...), target_userid: int = Form(...), proxy: str = Form(...),
                                    message_body: str = Form(...), clients: ClientStorage = Depends(get_clients), ):
    cl = clients.get(sessionid, proxy)
    result = cl.direct_send(message_body, [target_userid, ])
    return result


# @app.post('/direct/send_photo_by_id', tags=["direct"], responses={404: {"description": "Not found"}})
# async def send_direct_photo_by_id(sessionid: str = Form(...), path: str = Form('/fata.jpg'), user_id: list[int] = Form(...), clients: ClientStorage = Depends(get_clients)):
#     cl = clients.get(sessionid)
#     result = cl.direct_send_photo(path, user_id)
#     return result

# @app.post('/direct/send_photo_by_username', tags=["direct"], responses={404: {"description": "Not found"}})
# async def send_direct_photo_by_username(sessionid: str = Form(...), path: str = Form('/fata.jpg'), username: str = Form(...), clients: ClientStorage = Depends(get_clients)):
#     cl = clients.get(sessionid)
#     user_id = int(cl.user_id_from_username(username))
#     result = cl.direct_send_photo(path, user_id)
#     return result

# HASHTAG

@app.post('/hashtag/get_top_hashtags', tags=["hashtag"], responses={404: {"description": "Not found"}})
async def hashtag_top(sessionid: str = Form(...), name: str = Form(...), amount: int = Form(27), proxy: str = Form(...),
                      clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    return cl.hashtag_medias_top(name, amount)


@app.post('/hashtag/get_recent_hashtags', tags=["hashtag"], responses={404: {"description": "Not found"}})
async def hashtag_recent(sessionid: str = Form(...), name: str = Form(...), amount: int = Form(27),
                         proxy: str = Form(...),
                         clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    return cl.hashtag_medias_recent(name, amount)


@app.post('/hashtag/get_hashtag_info', tags=["hashtag"], responses={404: {"description": "Not found"}})
async def hashtag_info(sessionid: str = Form(...), name: str = Form(...), proxy: str = Form(...),
                       clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    result = cl.hashtag_info(
        name=name, )
    return result


# Highlight


@app.post('/highlight/user_highlights', tags=["highlight"], responses={404: {"description": "Not found"}})
async def hashtag_top(sessionid: str = Form(...), user_id: str = Form(...), amount: int = Form(5),
                      proxy: str = Form(...),
                      clients: ClientStorage = Depends(get_clients)):
    cl = clients.get(sessionid, proxy)
    return cl.user_highlights(user_id, amount)


# End Routers


@app.exception_handler(Exception)
async def handle_exception(request, exc: Exception):
    return JSONResponse({
        "detail": str(exc),
        "exc_type": str(type(exc).__name__)
    }, status_code=500)


def custom_openapi():
    # if app.openapi_schema:
    #     return app.openapi_schema
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
