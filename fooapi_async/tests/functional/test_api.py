from fooapi_async.tests.functional import BaseTest


class TestUsersHandler(BaseTest):
    def test_users_returned(self):
        data = self.fetch('/api/users')
