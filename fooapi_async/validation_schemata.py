import re
from os.path import expanduser
from typing import Optional

import phonenumbers
from pydantic import (BaseModel, validator, PositiveInt, EmailStr,
                      BaseSettings, constr)
from jwt import decode as jwt_decode, InvalidTokenError

from .models import (ContactTypeNameEnum, Contact as ContactModel,
                     User as UserModel)


class EmailOrEmptyStr(EmailStr):
    @classmethod
    def validate(cls, value: str):
        if isinstance(value, str) and not len(value):
            return value

        return super().validate(value)


class PhoneNumberStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('Phone number must be a string')

        # skip empty values (to allow us to clear the phone value)
        if not len(v):
            return v

        try:
            num = phonenumbers.parse(v)
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise ValueError(str(e))

        if not phonenumbers.is_possible_number(num):
            raise ValueError('Such phone number is impossible.')

        return v


class LimitOffset(BaseModel):
    limit: Optional[PositiveInt] = None
    offset: PositiveInt = None

    @validator('limit', always=True)
    def validate_limit(cls, v, **kwargs):
        # avoid cyclical import
        from .app import settings

        if v is None:
            return settings.paging_max_limit

        if v > settings.paging_max_limit:
            raise ValueError(
                f'limit must not be greater than {settings.paging_max_limit}')
        return v


class Contact(BaseModel):
    phone_no: PhoneNumberStr = ''
    email: EmailOrEmptyStr = ''
    type: ContactTypeNameEnum = ...

    @validator('phone_no')
    def validate_phone(cls, v, **kwargs):
        if len(v) > ContactModel.PHONE_MAX_LEN:
            raise ValueError(
                f'Maximum phone length is {ContactModel.PHONE_MAX_LEN}')

        return v

    @validator('email', always=True)
    def validate_email(cls, v, values, **kwargs):
        if len(v) > ContactModel.EMAIL_MAX_LEN:
            raise ValueError(
                f'Maximum email length is {ContactModel.EMAIL_MAX_LEN}')

        if not len(v) and not len(values.get('phone_no', '')):
            raise ValueError('Either phone number or email must be provided')

        if len(v) and len(values.get('phone_no', '')):
            raise ValueError('Only one of phone or email can be provided')

        return v

    @validator('type')
    def validate_type(cls, v, **kwargs):
        # replace user-friendly name with int value for database storage
        return int(ContactModel.NAMES_TO_TYPES[v])

    class Config:
        anystr_strip_whitespace = True


class User(BaseModel):
    name: constr(min_length=1, max_length=UserModel.NAME_MAX_LEN,
                 strip_whitespace=True) = ...


class Headers(BaseModel):
    Authorization: str = ...

    @validator('Authorization', always=True)
    def validate_jwt_token(cls, v, values, **kwargs):
        match = re.fullmatch(r'Bearer (?P<jwt>[A-Za-z0-9.\-_=]+)', v)
        try:
            # avoid cyclical import
            from .app import settings
            jwt = jwt_decode(match['jwt'], settings.pub_key,
                             algorithms='RS256')
            values['creator_id'] = jwt['id']
            return v
        except (InvalidTokenError, ValueError, TypeError):
            raise ValueError('Error while extracting creator id from JWT')
        except KeyError:
            raise ValueError('JWT not found in the Authorization header')


class Settings(BaseSettings):
    db_uri: str = ...
    api_port: PositiveInt = ...
    pub_key: str = ...
    priv_key: str = None
    paging_max_limit: PositiveInt = ...

    @validator('pub_key')
    def read_public_key(cls, v):
        try:
            with open(expanduser(v), 'r') as f:
                return f.read()
        except OSError:
            raise ValueError("Can't read the public key from the specified path")

    class Config:
        env_prefix = 'FOOAPI_'
