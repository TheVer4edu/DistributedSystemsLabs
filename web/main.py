from fastapi import FastAPI
from endpoints.links import router as links_router

app = FastAPI()

app.include_router(links_router, tags=['links'])


@app.get("/")
def app_root():
    return {"Hello": "World"}
