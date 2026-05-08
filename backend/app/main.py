import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routes import routers
from app.core.db import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)

for router in routers:
    app.include_router(router)
