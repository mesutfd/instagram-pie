from typing import List, Optional
from pathlib import Path
import requests
from instagrapi import Client
from .auth import auth_login, auth_relogin, settings_get
import json
from dependencies import get_clients
from storages import ClientStorage

from pydantic import AnyHttpUrl
from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.responses import FileResponse
from instagrapi.types import (
    Story, StoryHashtag, StoryLink,
    StoryLocation, StoryMention, StorySticker,
    Media, Location, Usertag
)

router = APIRouter(
    prefix='/instagram/engine/instagrapi/direct',
    tags=["direct"],
    responses={404: {'description': 'Not Found'}}
)


@router.post('/send_by_username')
def send_direct_message_by_username(
        sessionid: str = Form(...),
        target_username: str = Form(...),
        message_body: str = Form(...),
        clients: ClientStorage = Depends(get_clients),
):
    cl = clients.get(sessionid)
    taken_username = cl.user_id_from_username(target_username)
    taken_user_id = int(taken_username)
    result = cl.direct_send(message_body, [taken_user_id, ])
    return result


@router.post('/send_by_id')
def send_direct_message_by_username(
        sessionid: str = Form(...),
        target_userid: int = Form(...),
        message_body: str = Form(...),
        clients: ClientStorage = Depends(get_clients),
):
    cl = clients.get(sessionid)
    result = cl.direct_send(message_body, [target_userid, ])
    return result

# @router.post('/send_to_username_list')
# def send_direct_message_by_username_list(
#         sessionid: str = Form(...),
#         target_usernames_list: list[int] = Form(...),
#         message_body: str = Form(...),
#         clients: ClientStorage = Depends(get_clients),
#         ):
#     cl = clients.get(sessionid)
#     taken_users_id = []
#     for i in target_usernames_list:
#         taken_user_list_id = cl.user_id_from_username(i)
#         taken_users_id.append(int(taken_user_list_id))
#     result = cl.direct_send(message_body, taken_users_id)
#     return result


# @router.post('/send_to_id_list')
# def send_direct_message_by_username_list(
#         sessionid: str = Form(...),
#         target_ids_list: list[int] = Form(...),
#         message_body: str = Form(...),
#         clients: ClientStorage = Depends(get_clients),
# ):
#     cl = clients.get(sessionid)
#     taken_users_id = []
#     for i in target_ids_list:
#         taken_users_id.append(i)
#     result = cl.direct_send(message_body, taken_users_id)
#     return result
