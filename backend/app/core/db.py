import asyncpg
from typing import Union
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from app.config import settings


class Database:
    def __init__(self, dsn: Union[str, None] = None):
        self.dsn = str(dsn or settings.ASYNC_POSTGRES_DATABASE_URL)
        self.pool: Union[asyncpg.Pool, None] = None

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(
            dsn=self.dsn,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )

    async def disconnect(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    def get_pool(self) -> asyncpg.Pool:
        if self.pool is None:
            raise RuntimeError("Database pool is not initialized")
        return self.pool

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[asyncpg.Connection]:
        async with self.get_pool().acquire() as conn:
            yield conn

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[asyncpg.Connection]:
        async with self.connection() as conn:
            async with conn.transaction():
                yield conn


db = Database()
