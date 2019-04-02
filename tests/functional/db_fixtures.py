from dateutil import parser

from fooapi_async.models import ContactTypeEnum

fixtures = [
    {
        'name': 'Frank Foobar',
        'creator_id': 100,
        'created_at': parser.parse('2019-01-01T00:00:01'),
        'contacts': [
            {
                'phone_no': '111',
                'email': '',
                'type': ContactTypeEnum.home,
                'created_at': parser.parse('2019-01-01T00:00:02'),
            },
            {
                'phone_no': '',
                'email': 'foo@bar.com',
                'type': ContactTypeEnum.work,
                'created_at': parser.parse('2019-01-01T00:00:03'),
            }
        ]
    },
    {
        'name': 'Crash Coredump',
        'creator_id': 200,
        'contacts': [],
        'created_at': parser.parse('2019-01-01T00:00:04'),
    },
    {
        'name': 'John Doe',
        'creator_id': 300,
        'contacts': [],
        'created_at': parser.parse('2019-01-01T00:00:05'),
    }
]
