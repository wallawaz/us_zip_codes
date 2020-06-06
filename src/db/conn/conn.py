import asyncio
import asyncpg 

async def get_async_conn(user: str, database: str, host: str=None, password: str=None):
    loop = asyncio.get_event_loop()
    return await asyncpg.connect(loop=loop, user=user, password=password, database=database, host=host)