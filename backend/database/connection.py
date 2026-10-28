import logging

import asyncpg
from asyncpg import Connection, Pool
from decouple import config

logger = logging.getLogger('completec-backend')

async def connection_init(conn: Connection):
    await conn.execute("SET CLIENT_ENCODING to 'utf-8';")

class DbConnection:
    pool: Pool = None

    @classmethod
    async def initialize(cls):
        try:
            cls.pool = await asyncpg.create_pool(
                host = config('DATABASE_HOST'),
                database = config('DATABASE_NAME'),
                user = config('DATABASE_USERNAME'),
                password = config('DATABASE_PASSWORD'),
                port = config('DATABASE_PORT'),
                init = connection_init
            )
        except Exception as e:
            logger.error(f'Failed to initialize database pool: {e}')
            raise e
        else:
            logger.info('Database pool initialized')
    
    @classmethod
    async def cleanup(cls):
        """Clean up the database pool"""
        if cls.pool:
            cls.pool.terminate()
            cls.pool = None
            logger.info('Database pool terminated')
