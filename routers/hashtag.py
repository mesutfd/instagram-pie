from storages import ClientStorage

# @router.post('/get_top_hashtags')
async def hashtag_top(
        sessionid: str,
        name: str,
        amount: int,
        clients: ClientStorage

):
    cl = clients.get(sessionid)
    result = cl.hashtag_medias_top(
        name=name,
        amount=amount)
    return result

# @router.post('/get_recent_hashtags')
async def hashtag_recent(
        sessionid: str,
        name: str,
        amount: int,
        clients: ClientStorage
):
    cl = clients.get(sessionid)
    result = cl.hashtag_medias_recent(
        name=name,
        amount=amount)
    return result


# @router.post('/get_hashtag_info')
def hashtag_info(
        sessionid: str,
        name: str,
        clients: ClientStorage
):
    cl = clients.get(sessionid)
    result = cl.hashtag_info(
        name=name,)
    return result
