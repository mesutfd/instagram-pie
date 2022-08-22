import json
from typing import Optional, Dict
from dependencies import ClientStorage


async def auth_login(username: str,
                     password: str,
                     verification_code: Optional[str],
                     proxy: Optional[str],
                     locale: Optional[str],
                     timezone: Optional[str],
                     clients: ClientStorage) -> str:
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


async def auth_relogin(sessionid: str,
                       clients: ClientStorage) -> str:
    """Relogin by username and password (with clean cookies)
    """
    cl = clients.get(sessionid)
    result = cl.relogin()
    return result


async def settings_get(sessionid: str,
                   clients: ClientStorage) -> Dict:
    """Get client's settings
    """
    cl = clients.get(sessionid)
    return cl.get_settings()


async def settings_set(settings: str,
                       sessionid: Optional[str],
                       clients: ClientStorage) -> str:
    """Set client's settings
    """
    if sessionid != "":
        cl = clients.get(sessionid)
    else:
        cl = clients.client()
    cl.set_settings(json.loads(settings))
    cl.expose()
    clients.set(cl)
    return cl.sessionid

async def timeline_feed(sessionid: str,
                   clients: ClientStorage) -> Dict:
    """Get your timeline feed
    """
    cl = clients.get(sessionid)
    return cl.get_timeline_feed()
