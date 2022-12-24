from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

from fastapi.staticfiles import StaticFiles

from endpoints.links import router as links_router
from endpoints.tglogin import router as tglogin_router

app = FastAPI()

app.include_router(links_router, tags=['links'])
app.include_router(tglogin_router, tags=['tglogin'])
app.mount('/static', StaticFiles(directory='/appdata'), name='static')

app.openapi_url = '/api/openapi.json'

@app.get("/")
def app_root():
    return {"Hello": "World"}


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f'/api/{app.openapi_url}',
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=f'api/{app.swagger_ui_oauth2_redirect_url}',
        swagger_js_url="/api/swagger-ui-bundle.js",
        swagger_css_url="/api/swagger-ui.css",
    )
