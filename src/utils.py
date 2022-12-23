from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import motor.motor_asyncio as aiomotor

from src.settings import load_config


def setup_config(app: web.Application) -> None:
    app['config'] = load_config()


async def postgres_ctx(app: web.Application) -> None:
    conf = app['config']['postgres']
    url_db = f"postgresql+asyncpg://{conf['user']}:{conf['password']}@{conf['host']}/{conf['database']}"
    DBSession = sessionmaker(bind=create_async_engine(url_db), class_=AsyncSession, expire_on_commit=False)
    session = DBSession()
    app['db_pg'] = session
    yield

    app['db_pg'].close()
    await app['db_pg'].wait_closed()


async def init_mongo(conf):
    mongo_uri = f"mongodb://{conf['host']}:{conf['port']}/{conf['database']}"
    conn = aiomotor.AsyncIOMotorClient(
        mongo_uri,
        maxPoolSize=conf['max_pool_size']
    )
    db_name = conf['database']
    return conn[db_name]


async def mongo_ctx(app):
    mongo = await init_mongo(app['config']['mongo'])
    app['db_mg'] = mongo
    yield

    app['db_mg'].client.close()


