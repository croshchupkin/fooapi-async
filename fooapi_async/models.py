from typing import Dict, Any
from enum import IntEnum, Enum
from datetime import datetime

from tortoise import Model, fields


class ContactTypeEnum(IntEnum):
    home = 1
    work = 2
    other = 3


class ContactTypeNameEnum(str, Enum):
    home = 'home'
    work = 'work'
    other = 'other'


class Contact(Model):
    TYPES_TO_NAMES = {
        ContactTypeEnum.home: ContactTypeNameEnum.home,
        ContactTypeEnum.work: ContactTypeNameEnum.work,
        ContactTypeEnum.other: ContactTypeNameEnum.other
    }
    NAMES_TO_TYPES = {v: k for k, v in TYPES_TO_NAMES.items()}

    PHONE_MAX_LEN = 30
    EMAIL_MAX_LEN = 128

    id = fields.IntField(pk=True)
    phone_no = fields.CharField(PHONE_MAX_LEN, null=False, default='')
    email = fields.CharField(EMAIL_MAX_LEN, null=False, default='')
    created_at = fields.DatetimeField(null=False, default=datetime.utcnow,
                                      index=True)
    type = fields.SmallIntField(null=False, default=ContactTypeEnum.other)
    user = fields.ForeignKeyField('models.User', related_name='contacts',
                                  on_delete=fields.CASCADE, null=False)

    def __repr__(self) -> str:
        return ('<Contact id={id}, phone_no={phone}, email={email}, '
                'type={type}, created_at={created_at}>').format(
                    id=self.id,
                    phone=self.phone_no,
                    email=self.email,
                    type=self.TYPES_TO_NAMES[self.type],
                    created_at=self.created_at.isoformat())

    def as_dict(self):
        return {
            'id': self.id,
            'phone_no': self.phone_no,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'type': self.TYPES_TO_NAMES[self.type]
        }


class User(Model):
    NAME_MAX_LEN = 128

    id = fields.IntField(pk=True)
    name = fields.CharField(NAME_MAX_LEN, null=False, required=True)
    created_at = fields.DatetimeField(null=False, default=datetime.utcnow,
                                      index=True)
    creator_id = fields.IntField(null=False)

    def __repr__(self) -> str:
        return (
            '<User id={id}, name={name}, created_at={created_at}, '
            'creator_id={creator_id}, contacts=[{contacts}]>').format(
                id=self.id,
                name=self.name,
                created_at=self.created_at.isoformat,
                creator_id=self.creator_id,
                contacts=', '.join((repr(c) for c in self.contacts)))

    def as_dict(self, dump_contacts=False) -> Dict[str, Any]:
        res = {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'contacts': [c.as_dict() for c in self.contacts]
        }

        return res
