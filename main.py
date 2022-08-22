from sys import prefix
import pkg_resources

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import RedirectResponse, JSONResponse
from routers import (
    auth, media, video, photo, user,
    igtv, clip, album, story,
    insights, send_direct, hashtag
)

app = FastAPI()

app.include_router(auth.router,prefix = '/auth')
app.include_router(media.router,prefix = '/instagram/engine/instagrapi')
app.include_router(video.router,prefix = '/instagram/engine/instagrapi')
app.include_router(photo.router,prefix = '/instagram/engine/instagrapi')
app.include_router(user.router,prefix = '/instagram/engine/instagrapi')
app.include_router(igtv.router,prefix = '/instagram/engine/instagrapi')
app.include_router(clip.router,prefix = '/instagram/engine/instagrapi')
app.include_router(album.router,prefix = '/instagram/engine/instagrapi')
app.include_router(story.router,prefix = '/instagram/engine/instagrapi')
app.include_router(insights.router,prefix = '/instagram/engine/instagrapi')
app.include_router(send_direct.router,prefix = '/instagram/engine/instagrapi')
app.include_router(hashtag.router,prefix = '/instagram/engine/instagrapi')



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
