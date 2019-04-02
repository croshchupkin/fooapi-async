import json
from os.path import expanduser
from urllib.parse import urlencode
from typing import Dict, Any

from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase
from tortoise import Tortoise
import jwt

from fooapi_async.app import (
    make_app,
    init_db,
    close_db_connections,
    init_settings)
from fooapi_async.routes import routes
from fooapi_async.models import User, Contact
from tests.functional.db_fixtures import fixtures


class BaseTest(AsyncHTTPTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        init_settings('settings-test.json')

    def get_app(self) -> Application:
        return make_app(routes)

    def setUp(self) -> None:
        super().setUp()
        self.io_loop.run_sync(init_db_and_apply_db_fixtures)

    def tearDown(self) -> None:
        self.io_loop.run_sync(close_db_connections)
        super().tearDown()

    def _do_request_and_assert(self, method: str, url: str, status_code: int,
                               ret_data: Dict[str, Any] = None,
                               body: Dict[str, Any] = None,
                               headers: Dict[str, Any] = None) -> None:
        if body is not None:
            body = urlencode(body)

        response = self.fetch(url, method=method, body=body,
                              headers=headers, raise_error=False)
        self.assertEqual(response.code, status_code)

        if ret_data is not None:
            res = json.loads(response.body)
            self.assertEqual(ret_data, res)

    def _create_token(self, creator_id: int) -> str:
        from fooapi_async.app import settings
        with open(expanduser(settings.priv_key), 'r') as f:
            priv_key = f.read()
        return jwt.encode({'id': creator_id}, priv_key,
                          algorithm='RS256').decode('utf8')

    def do_get_and_assert(self, url: str, status_code: int,
                          ret_data: Dict[str, Any]) -> None:
        self._do_request_and_assert('GET', url, status_code, ret_data)

    def do_post_and_assert(self, url: str, status_code: int,
                           ret_data: Dict[str, Any], body: Dict[str, Any],
                           creator_id: int = None) -> None:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if creator_id is not None:
            headers['Authorization'] = 'Bearer {}'.format(
                self._create_token(creator_id))

        self._do_request_and_assert('POST', url, status_code, ret_data, body,
                                    headers)

    def do_put_and_assert(self, url: str, status_code: int,
                          ret_data: Dict[str, Any], body: Dict[str, Any],
                          creator_id: int) -> None:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if creator_id is not None:
            headers['Authorization'] = 'Bearer {}'.format(
                self._create_token(creator_id))

        self._do_request_and_assert('PUT', url, status_code, ret_data, body,
                                    headers)

    def do_delete_and_assert(self, url: str, status_code: int,
                             creator_id: int) -> None:
        if creator_id is not None:
            headers = {'Authorization': 'Bearer {}'.format(
                self._create_token(creator_id))}
        else:
            headers = None
        self._do_request_and_assert('DELETE', url, status_code,
                                    headers=headers)


async def init_db_and_apply_db_fixtures() -> None:
    from fooapi_async.app import settings
    await init_db(settings)
    await Tortoise.generate_schemas()

    for item in fixtures:
        user = await User.create(name=item['name'],
                                 creator_id=item['creator_id'],
                                 created_at=item['created_at'])
        for c in item['contacts']:
            await Contact.create(**c, user=user)
