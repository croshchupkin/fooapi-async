from fooapi_async.models import ContactTypeEnum

fixtures = [
    {
        'name': 'Frank Foobar',
        'creator_id': 100,
        'contacts': [
            {
                'phone_no': '111',
                'email': '',
                'type': ContactTypeEnum.home
            },
            {
                'phone_no': '',
                'email': 'foo@bar.com',
                'type': ContactTypeEnum.work
            }
        ]
    },
    {
        'name': 'Crash Coredump',
        'creator_id': 200,
        'contacts': []
    },
    {
        'name': 'John Doe',
        'creator_id': 300,
        'contacts': []
    }
]
