from typing import Optional, Tuple, List, Any, Dict

from tortoise.queryset import QuerySet
from tortoise.exceptions import DoesNotExist

from .models import Contact, User


class UserNotFound(Exception):
    def __init__(self, user_id):
        super().__init__(f'User with id {user_id} was not found')


class ContactNotFound(Exception):
    def __init__(self, contact_id):
        super().__init__(f'Contact with id {contact_id} was not found')


async def get_user_list(
        limit: Optional[int] = None,
        offset: Optional[int] = None) -> Tuple[List[User], int]:
    qry = User\
        .all()\
        .order_by('created_at')\
        .prefetch_related('contacts')

    users = await _limit_and_offset_query(qry, limit, offset)

    user_count = await User.all().count()

    return users, user_count


async def get_single_user(user_id: int) -> User:
    return await _fetch_single_user(user_id, prefetch_contacts=True)


async def update_user(user_id: int, **data) -> None:
    user = await _fetch_single_user(user_id)
    for name, val in data.items():
        setattr(user, name, val)
    await user.save()


async def delete_single_user(user_id: int) -> None:
    user = await _fetch_single_user(user_id)
    await user.delete()


async def get_single_contact(contact_id: int) -> Contact:
    return await _fetch_single_contact(contact_id)


async def update_contact(contact_id: int, **data) -> None:
    contact = await _fetch_single_contact(contact_id)
    for name, val in data.items():
        setattr(contact, name, val)
    await contact.save()


async def delete_single_contact(contact_id: int) -> None:
    contact = await _fetch_single_contact(contact_id)
    await contact.delete()


async def get_user_contacts(
        user_id: int, limit: Optional[int] = None,
        offset: Optional[int] = None) -> Tuple[List[Contact], int]:
    await _fetch_single_user(user_id)

    qry = Contact.filter(user_id=user_id)
    contacts = await _limit_and_offset_query(qry, limit, offset)
    total = await qry.count()

    return contacts, total


async def add_user(**data) -> int:
    user = await User.create(**data)
    return user.id


async def add_user_contact(user_id: int, **contact_data) -> int:
    user = await _fetch_single_user(user_id)

    new_contact = await Contact.create(user=user, **contact_data)

    return new_contact.id


async def delete_all_user_contacts(user_id: int) -> None:
    await _fetch_single_user(user_id)
    await Contact.filter(user_id=user_id).delete()


async def _fetch_single_user(user_id: int,
                             prefetch_contacts: bool = False) -> User:
    qry = User.get(id=user_id)
    if prefetch_contacts:
        qry = qry.prefetch_related('contacts')

    try:
        return await qry
    except DoesNotExist:
        raise UserNotFound(user_id) from None


async def _fetch_single_contact(contact_id: int) -> Contact:
    try:
        return await Contact.get(id=contact_id)
    except DoesNotExist:
        raise ContactNotFound(contact_id) from None


def _limit_and_offset_query(qry: QuerySet, limit: Optional[int],
                            offset: Optional[int]) -> QuerySet:
    if limit is not None:
        qry = qry.limit(limit)
    if offset is not None:
        qry = qry.offset(offset)
    return qry
