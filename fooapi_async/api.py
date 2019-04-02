from tornado.web import RequestHandler

from .utils import (
    bad_request_on_validation_error,
    prepare_request_arguments,
    not_found_on_exception,
    unathorized_on_authorization_error,
    ensure_contact_can_be_edited,
    ensure_user_can_be_edited,
    ensure_user_contacts_can_be_edited)
from .validation_schemata import User, LimitOffset, Contact, Headers
from .database_operations import (
    get_user_list,
    add_user,
    get_user_contacts,
    add_user_contact,
    UserNotFound,
    update_user,
    delete_all_user_contacts,
    get_single_user,
    delete_single_user,
    ContactNotFound,
    get_single_contact,
    update_contact,
    delete_single_contact)


class UsersHandler(RequestHandler):
    @bad_request_on_validation_error
    async def get(self) -> None:
        args = LimitOffset.parse_obj(
            prepare_request_arguments(self.request.query_arguments))

        users, user_count = await get_user_list(**args.dict())
        self.write({
            'total': user_count,
            'result': [u.as_dict() for u in users]
        })

    @bad_request_on_validation_error
    async def post(self) -> None:
        headers = Headers.parse_obj(dict(self.request.headers.items()))
        args = User.parse_obj(
            prepare_request_arguments(self.request.body_arguments))

        new_id = await add_user(creator_id=headers.creator_id,
                                **args.dict())

        self.set_status(201)
        self.write({
            'result': {'user_id': new_id}
        })


class ContactsHandler(RequestHandler):
    @bad_request_on_validation_error
    @not_found_on_exception(UserNotFound)
    async def get(self, user_id: str) -> None:
        args = LimitOffset.parse_obj(
            prepare_request_arguments(self.request.query_arguments))

        contacts, contact_count = await get_user_contacts(int(user_id),
                                                          **args.dict())

        self.write({
            'total': contact_count,
            'result': [c.as_dict() for c in contacts]
        })

    @unathorized_on_authorization_error
    @bad_request_on_validation_error
    @not_found_on_exception(UserNotFound)
    @ensure_user_contacts_can_be_edited
    async def post(self, user_id: str) -> None:
        args = Contact.parse_obj(
            prepare_request_arguments(self.request.body_arguments))

        new_id = await add_user_contact(int(user_id), **args.dict())

        self.set_status(201)
        self.write({
            'result': {'contact_id': new_id}
        })

    @unathorized_on_authorization_error
    @bad_request_on_validation_error
    @not_found_on_exception(UserNotFound)
    @ensure_user_contacts_can_be_edited
    async def delete(self, user_id: str) -> None:
        await delete_all_user_contacts(int(user_id))
        self.set_status(204)


class SingleUserHandler(RequestHandler):
    @not_found_on_exception(UserNotFound)
    async def get(self, user_id: str) -> None:
        user = await get_single_user(int(user_id))
        self.write({
            'result': user.as_dict()
        })

    @unathorized_on_authorization_error
    @bad_request_on_validation_error
    @not_found_on_exception(UserNotFound)
    @ensure_user_can_be_edited
    async def put(self, user_id: str) -> None:
        args = User.parse_obj(
            prepare_request_arguments(self.request.body_arguments))
        await update_user(int(user_id), **args.dict())
        self.set_status(204)

    @unathorized_on_authorization_error
    @bad_request_on_validation_error
    @not_found_on_exception(UserNotFound)
    @ensure_user_can_be_edited
    async def delete(self, user_id: str) -> None:
        await delete_single_user(int(user_id))
        self.set_status(204)


class SingleContactHandler(RequestHandler):
    @not_found_on_exception(ContactNotFound)
    async def get(self, contact_id: str) -> None:
        contact = await get_single_contact(int(contact_id))
        self.write({
            'result': contact.as_dict()
        })

    @unathorized_on_authorization_error
    @bad_request_on_validation_error
    @not_found_on_exception(ContactNotFound)
    @ensure_contact_can_be_edited
    async def put(self, contact_id: str) -> None:
        args = Contact.parse_obj(
            prepare_request_arguments(self.request.body_arguments))
        await update_contact(int(contact_id), **args.dict())
        self.set_status(204)

    @unathorized_on_authorization_error
    @bad_request_on_validation_error
    @not_found_on_exception(ContactNotFound)
    @ensure_contact_can_be_edited
    async def delete(self, contact_id: str) -> None:
        await delete_single_contact(int(contact_id))
        self.set_status(204)
