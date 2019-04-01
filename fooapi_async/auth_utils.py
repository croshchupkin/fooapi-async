from typing import Union

from .database_operations import (
    get_single_user,
    get_single_contact,
    UserNotFound,
    ContactNotFound)


class AuthorizationError(Exception):
    pass


async def ensure_can_edit_user(user_id: int, creator_id: int) -> None:
    auth_error = AuthorizationError(f"Creator {creator_id} can't edit user {user_id}")
    try:
        user = await get_single_user(user_id)
    except UserNotFound:
        raise auth_error from None

    if user.creator_id != creator_id:
        raise auth_error from None


async def ensure_can_edit_contact(contact_id: int, creator_id: int) -> None:
    auth_error = AuthorizationError(f"Creator {creator_id} can't edit contact {contact_id}")

    try:
        contact = await get_single_contact(contact_id)
    except ContactNotFound:
        raise auth_error from None

    if contact.user.creator_id != creator_id:
        raise auth_error from None
