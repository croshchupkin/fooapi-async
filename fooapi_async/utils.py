from functools import wraps

from pydantic import ValidationError

from .auth_utils import (
    AuthorizationError,
    ensure_can_edit_contact,
    ensure_can_edit_user)
from .validation_schemata import Headers


def http_code_on_exception(http_code, exc, message_factory=lambda e: str(e)):
    def wrapper(method):
        @wraps(method)
        async def new_meth(self, *args, **kwargs):
            try:
                await method(self, *args, **kwargs)
            except exc as e:
                self.set_status(http_code)
                self.write({'result': message_factory(e)})
        return new_meth
    return wrapper


def not_found_on_exception(exc):
    return http_code_on_exception(404, exc)


def bad_request_on_validation_error(method):
    return http_code_on_exception(400, ValidationError, lambda e: e.errors())(method)


def unathorized_on_authorization_error(method):
    return http_code_on_exception(401, AuthorizationError)(method)


def ensure_user_can_be_edited(method):
    @wraps(method)
    async def wrapper(self, user_id, *args, **kwargs):
        headers = Headers.parse_obj(dict(self.request.headers.items()))
        await ensure_can_edit_user(int(user_id))
        await method(self, user_id, headers.creator_id, *args, **kwargs)
    return wrapper


def ensure_contact_can_be_edited(method):
    @wraps(method)
    async def wrapper(self, contact_id, *args, **kwargs):
        headers = Headers.parse_obj(dict(self.request.headers.items()))
        await ensure_can_edit_user(int(contact_id), headers.creator_id)
        await method(self, contact_id, *args, **kwargs)
    return wrapper


def prepare_request_arguments(args):
    """
    Flattens request arguments by taking only the first value for each
    argument name and converts bytes values to str
    """
    args = {k: v[0] for k, v in args.items() if len(v)}
    for k, v in args.items():
        if isinstance(v, bytes):
            args[k] = v.decode('utf8')
    return args
