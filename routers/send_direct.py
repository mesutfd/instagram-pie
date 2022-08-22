from dependencies import get_clients
from storages import ClientStorage

from pathlib import Path

# @router.post('/send_by_username')
async def send_direct_message_by_username(
        sessionid: str,
        target_username: str,
        message_body: str,
        clients: ClientStorage
):
    cl = clients.get(sessionid)
    taken_username = cl.user_id_from_username(target_username)
    taken_user_id = int(taken_username)
    result = cl.direct_send(message_body, [taken_user_id, ])
    return result


# @router.post('/send_by_id')
async def send_direct_message_by_id(
        sessionid: str,
        target_userid: int,
        message_body: str,
        clients: ClientStorage
):
    cl = clients.get(sessionid)
    result = cl.direct_send(message_body, [target_userid, ])
    return result

async def send_direct_photo_by_id(sessionid: str, path: Path, user_id: int, clients: ClientStorage):
    cl = clients.get(sessionid)
    result = cl.direct_send_photo(path, user_id)
    return result

async def send_direct_photo_by_username(sessionid: str, path: Path, username: str, clients: ClientStorage):
    cl = clients.get(sessionid)
    user_id = cl.user_id_from_username(username)
    result = cl.direct_send_photo(path, user_id)
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
