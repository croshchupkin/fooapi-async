from typing import List, Tuple

from tortoise import Tortoise
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

from .validation_schemata import Settings
from .routes import routes


settings = None


def init_settings(settings_file_path: str) -> Settings:
    global settings
    settings = Settings.parse_file(settings_file_path)


async def init_db(settings: Settings) -> None:
    await Tortoise.init(
        db_url=settings.db_uri,
        modules={'models': ['fooapi_async.models']}
    )


async def close_db_connections() -> None:
    await Tortoise.close_connections()


async def create_schema() -> None:
    try:
        global settings
        await init_db(settings)
        await Tortoise.generate_schemas(safe=False)
    finally:
        await close_db_connections()


async def drop_schema() -> None:
    global settings
    await init_db(settings)
    await Tortoise._drop_databases()


def make_app(routes: List[Tuple[str, RequestHandler]]) -> Application:
    return Application(routes)


def run(settings_file_path: str) -> None:
    global settings

    init_settings(settings_file_path)

    loop = IOLoop.current()

    async def run_db_init():
        await init_db(settings)

    try:
        loop.run_sync(run_db_init)

        application = make_app(routes)
        application.listen(settings.api_port)

        loop.start()
    finally:
        loop.run_sync(close_db_connections)
