from .database_operations import (
    get_single_user,
    get_single_contact)


class AuthorizationError(Exception):
    pass


async def ensure_can_edit_user(user_id: int, creator_id: int) -> None:
    auth_error = AuthorizationError(f"Creator {creator_id} can't edit user {user_id}")
    user = await get_single_user(user_id)

    if user.creator_id != creator_id:
        raise auth_error from None


async def ensure_can_edit_contact(contact_id: int, creator_id: int) -> None:
    auth_error = AuthorizationError(f"Creator {creator_id} can't edit contact {contact_id}")

    contact = await get_single_contact(contact_id)
    await contact.fetch_related('user')

    if contact.user.creator_id != creator_id:
        raise auth_error from None
