from .api import (
    UsersHandler,
    ContactsHandler,
    SingleContactHandler,
    SingleUserHandler)

routes = [
    (r'/api/users/(\d+)/contacts', ContactsHandler),
    (r'/api/users/(\d+)', SingleUserHandler),
    (r'/api/contacts/(\d+)', SingleContactHandler),
    (r'/api/users', UsersHandler),
]
