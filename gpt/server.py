from fastapi import FastAPI

from gpt.endpoints import router


def create_server() -> FastAPI:
    app = FastAPI()

    app.include_router(router)

    return app
