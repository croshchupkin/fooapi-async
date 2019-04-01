from tornado.testing import AsyncHTTPTestCase
from tortoise import Tortoise

from fooapi_async.app import (
    make_app,
    init_db,
    close_db_connections,
    init_settings)
from fooapi_async.routes import routes
from fooapi_async.models import User, Contact
from fooapi_async.tests.functional.db_fixtures import fixtures


class BaseTest(AsyncHTTPTestCase):
    @classmethod
    def setUpClass(cls):
        init_settings('settings-test.json')

    def get_app(self):
        return make_app(routes)

    def setUp(self):
        super().setUp()
        self.io_loop.run_sync(init_db_and_apply_db_fixtures)

    def tearDown(self):
        self.io_loop.run_sync(close_db_connections)
        super().tearDown()


async def init_db_and_apply_db_fixtures():
    from fooapi_async.app import settings
    await init_db(settings)
    await Tortoise.generate_schemas()

    for item in fixtures:
        user = await User.create(name=item['name'],
                                 creator_id=item['creator_id'])
        for c in item['contacts']:
            await Contact.create(**c, user=user)
