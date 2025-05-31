from fastapi import FastAPI

from api.endpoints import router


def create_server() -> FastAPI:
    app = FastAPI()

    app.include_router(router)

    return app
