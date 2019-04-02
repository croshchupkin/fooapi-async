from tests.functional import BaseTest


class UsersHandlerTest(BaseTest):
    def test_users_returned(self):
        self.do_get_and_assert(
            '/api/users',
            200,
            {
                'result': [
                    {
                        'id': 1,
                        'name': 'Frank Foobar',
                        'created_at': '2019-01-01T00:00:01',
                        'contacts': [
                            {
                                'id': 1,
                                'phone_no': '111',
                                'email': '',
                                'type': 'home',
                                'created_at': '2019-01-01T00:00:02',
                            },
                            {
                                'id': 2,
                                'phone_no': '',
                                'email': 'foo@bar.com',
                                'type': 'work',
                                'created_at': '2019-01-01T00:00:03'
                            }
                        ]
                    },
                    {
                        'id': 2,
                        'name': 'Crash Coredump',
                        'contacts': [],
                        'created_at': '2019-01-01T00:00:04'
                    }
                ],
                'total': 3
            })

    def test_users_limited_and_offset(self):
        self.do_get_and_assert(
            '/api/users?limit=1&offset=2',
            200,
            {
                'result': [
                    {
                        'id': 3,
                        'name': 'John Doe',
                        'contacts': [],
                        'created_at': '2019-01-01T00:00:05'
                    }
                ],
                'total': 3
            })

    def test_limit_offset_validated(self):
        self.do_get_and_assert(
            '/api/users?limit=-1&offset=-2',
            400,
            {
                'result': [
                    {
                        'ctx': {'limit_value': 0},
                        'loc': ['limit'],
                        'msg': 'ensure this value is greater than 0',
                        'type': 'value_error.number.not_gt'
                    },
                    {
                        'loc': ['limit'],
                        'msg': 'value is not none',
                        'type': 'type_error.none.allowed'
                    },
                    {
                        'ctx': {'limit_value': 0},
                        'loc': ['offset'],
                        'msg': 'ensure this value is greater than 0',
                        'type': 'value_error.number.not_gt'
                    }
                ]
            })

    def test_user_created(self):
        self.do_post_and_assert(
            '/api/users',
            201,
            {'result': {'user_id': 4}},
            {'name': 'Baz'},
            1)

    def test_user_name_required(self):
        self.do_post_and_assert(
            '/api/users',
            400,
            {
                'result': [
                    {
                        'loc': ['name'],
                        'msg': 'field required',
                        'type': 'value_error.missing'
                    }
                ]
            },
            {},
            1)

    def test_jwt_required(self):
        self.do_post_and_assert(
            '/api/users',
            400,
            {
                'result': [
                    {
                        'loc': ['Authorization'],
                        'msg': 'field required',
                        'type': 'value_error.missing'
                    }
                ]
            },
            {'name': 'Baz'})


class ContactsHandlerTest(BaseTest):
    def test_contacts_returned(self):
        self.do_get_and_assert(
            '/api/users/1/contacts',
            200,
            {
                'result': [
                    {
                        'id': 1,
                        'phone_no': '111',
                        'email': '',
                        'type': 'home',
                        'created_at': '2019-01-01T00:00:02',
                    },
                    {
                        'id': 2,
                        'phone_no': '',
                        'email': 'foo@bar.com',
                        'type': 'work',
                        'created_at': '2019-01-01T00:00:03',
                    }
                ],
                'total': 2
            })

    def test_404_on_nonexistent_user_id(self):
        self.do_get_and_assert(
            '/api/users/1000/contacts',
            404,
            {'result': 'User with id 1000 was not found'})

    def test_contacts_limited_and_offset(self):
        self.do_get_and_assert(
            '/api/users/1/contacts?limit=1&offset=1',
            200,
            {
                'result': [
                    {
                        'id': 2,
                        'phone_no': '',
                        'email': 'foo@bar.com',
                        'type': 'work',
                        'created_at': '2019-01-01T00:00:03',
                    }
                ],
                'total': 2
            })

    def test_contact_is_added(self):
        self.do_post_and_assert(
            '/api/users/1/contacts',
            201,
            {'result': {'contact_id': 3}},
            {'email': 'ddd@bbb.com', 'type': 'work'},
            100)

        self.do_post_and_assert(
            '/api/users/2/contacts',
            201,
            {'result': {'contact_id': 4}},
            {'phone_no': '+380111111111', 'type': 'work'},
            200)

    def test_contact_data_is_validated(self):
        self.do_post_and_assert(
            '/api/users/1/contacts',
            400,
            {
                'result': [
                    {
                        'loc': ['email'],
                        'msg': 'Either phone number or email must be provided',
                        'type': 'value_error'
                    },
                    {
                        'loc': ['type'],
                        'msg': 'field required',
                        'type': 'value_error.missing'
                    }
                ]
            },
            {},
            100)

        self.do_post_and_assert(
            '/api/users/1/contacts',
            400,
            {
                'result': [
                    {
                        'loc': ['phone_no'],
                        'msg': 'Such phone number is impossible.',
                        'type': 'value_error'},
                    {
                        'loc': ['email'],
                        'msg': 'Either phone number or email must be provided',
                        'type': 'value_error'
                    }
                ]
            },
            {'phone_no': '+180111111111', 'type': 'work'},
            100)

        self.do_post_and_assert(
            '/api/users/1/contacts',
            400,
            {
                'result': [
                    {
                        'loc': ['email'],
                        'msg': 'Only one of phone or email can be provided',
                        'type': 'value_error'
                    }
                ]
            },
            {'phone_no': '+380111111111', 'email': 'baz@bar.com',
             'type': 'work'},
            100)

    def test_401_on_invalid_creator_id(self):
        self.do_post_and_assert(
            '/api/users/1/contacts',
            401,
            {'result': "Creator 1000 can't edit user 1"},
            {'email': 'ddd@bbb.com', 'type': 'work'},
            1000)

        self.do_delete_and_assert(
            '/api/users/1/contacts',
            401,
            1000)

    def test_contacts_are_deleted(self):
        self.do_delete_and_assert(
            '/api/users/1/contacts',
            204,
            100)

        self.do_get_and_assert(
            '/api/users/1/contacts',
            200,
            {'result': [], 'total': 0})


class SingleUserHandlerTest(BaseTest):
    def test_user_returned(self):
        self.do_get_and_assert(
            '/api/users/1',
            200,
            {
                'result': {
                    'id': 1,
                    'name': 'Frank Foobar',
                    'created_at': '2019-01-01T00:00:01',
                    'contacts': [
                        {
                            'id': 1,
                            'phone_no': '111',
                            'email': '',
                            'type': 'home',
                            'created_at': '2019-01-01T00:00:02',
                        },
                        {
                            'id': 2,
                            'phone_no': '',
                            'email': 'foo@bar.com',
                            'type': 'work',
                            'created_at': '2019-01-01T00:00:03',
                        }
                    ]
                }
            })

    def test_404_on_nonexistent_user_id(self):
        self.do_get_and_assert(
            '/api/users/1000',
            404,
            {'result': 'User with id 1000 was not found'})

        self.do_put_and_assert(
            '/api/users/1000',
            404,
            {'result': 'User with id 1000 was not found'},
            {'name': 'ffff'},
            100)

        self.do_delete_and_assert(
            '/api/users/1000',
            404,
            100)

    def test_401_on_invalid_creator_id(self):
        self.do_put_and_assert(
            '/api/users/1',
            401,
            {'result': "Creator 1000 can't edit user 1"},
            {'name': 'zzz'},
            1000)

        self.do_delete_and_assert(
            '/api/users/1',
            401,
            1000)

    def test_user_updated(self):
        self.do_put_and_assert(
            '/api/users/1',
            204,
            None,
            {'name': 'Zack'},
            100)

    def test_user_data_validated(self):
        self.do_put_and_assert(
            '/api/users/1',
            400,
            {
                'result': [
                    {
                        'loc': ['name'],
                        'msg': 'field required',
                        'type': 'value_error.missing'
                    }
                ]
            },
            {},
            100)

    def test_user_deleted(self):
        self.do_delete_and_assert(
            '/api/users/1',
            204,
            100)

        self.do_get_and_assert(
            '/api/users',
            200,
            {
                'result': [
                    {
                        'id': 2,
                        'name': 'Crash Coredump',
                        'contacts': [],
                        'created_at': '2019-01-01T00:00:04',
                    },
                    {
                        'id': 3,
                        'name': 'John Doe',
                        'contacts': [],
                        'created_at': '2019-01-01T00:00:05',
                    }
                ],
                'total': 2
            })

class SingleContactHandlerTest(BaseTest):
    def test_contact_returned(self):
        self.do_get_and_assert(
            '/api/contacts/1',
            200,
            {
                'result': {
                    'id': 1,
                    'phone_no': '111',
                    'email': '',
                    'type': 'home',
                    'created_at': '2019-01-01T00:00:02',
                }
            })

    def test_404_on_nonexistent_user_id(self):
        self.do_get_and_assert(
            '/api/contacts/1000',
            404,
            {'result': 'Contact with id 1000 was not found'})

        self.do_put_and_assert(
            '/api/contacts/1000',
            404,
            {'result': 'Contact with id 1000 was not found'},
            {'phone_no': '+380111111111', 'type': 'work'},
            100)

        self.do_delete_and_assert(
            '/api/contacts/1000',
            404,
            100)

    def test_401_on_invalid_creator_id(self):
        self.do_put_and_assert(
            '/api/contacts/1',
            401,
            {'result': "Creator 1000 can't edit contact 1"},
            {'phone_no': '+380111111111', 'type': 'work'},
            1000)

        self.do_delete_and_assert(
            '/api/contacts/1',
            401,
            1000)

    def test_contact_updated(self):
        self.do_put_and_assert(
            '/api/contacts/1',
            204,
            None,
            {'phone_no': '+380111111111', 'type': 'work'},
            100)

    def test_contact_data_validated(self):
        self.do_put_and_assert(
            '/api/contacts/1',
            400,
            {
                'result': [
                    {
                        'loc': ['email'],
                        'msg': 'Either phone number or email must be provided',
                        'type': 'value_error'
                    },
                    {
                        'loc': ['type'],
                        'msg': 'field required',
                        'type': 'value_error.missing'
                    }
                ]
            },
            {},
            100)

    def test_contact_deleted(self):
        self.do_delete_and_assert(
            '/api/contacts/1',
            204,
            100)

        self.do_get_and_assert(
            '/api/users/1/contacts',
            200,
            {
                'result': [
                    {
                        'id': 2,
                        'phone_no': '',
                        'email': 'foo@bar.com',
                        'type': 'work',
                        'created_at': '2019-01-01T00:00:03',
                    }
                ],
                'total': 1
            })
