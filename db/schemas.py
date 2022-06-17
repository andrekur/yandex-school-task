from pydantic import BaseModel, UUID4, PositiveInt, constr, validator, conint
from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status


def convert_datetime_to_iso_8601(dt: datetime) -> str:
    """
    Convert date to iso 8601
    """
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def transform_to_utc_datetime(dt: datetime) -> datetime:
    """
    Convert date to utc
    """
    return dt.astimezone(tz=timezone.utc)


class TypeItems(str, Enum):
    """
    Descriptions type items
    """
    product = 'OFFER'
    category = 'CATEGORY'

    def __str__(self):
        return "%s" % self._value_


class _ItemsBase(BaseModel):
    """
    Base serializer class for input items
    """
    id: UUID4
    name: constr(min_length=1)
    parentId: UUID4 = None
    price: conint(ge=0) = None
    type: TypeItems


class ItemIn(BaseModel):
    """
    Serializer items out
    """
    items: List[_ItemsBase]
    updateDate: datetime

    _normalize_datetime = validator(
        "updateDate",
        allow_reuse=True)(transform_to_utc_datetime)

    class Config:
        json_encoders = {
            datetime: convert_datetime_to_iso_8601
        }
        orm_mode = True
        error_msg_templates = {
            'Validation Failed',
        }

    @validator('items')
    def check_unique_ids(cls, items):
        ids = [str(element.id) for element in items]

        if len(ids) != len(set(ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Validation Failed')
        del ids

        return items

    @validator('items')
    def check_price(cls, items):
        for element in items:
            if (element.price is None and element.type == TypeItems.product) or\
                    (element.price is not None and element.type == TypeItems.category):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Validation Failed')
        return items


class ItemIdIn(BaseModel):
    """
    Serializer item id
    """
    id: UUID4

    class Config:
        orm_mode = True


class ItemsOut(BaseModel):
    """
    Serializer items out
    """
    id: UUID4
    name: constr(min_length=1)
    parentId: UUID4 = None
    price: conint(ge=0) = None
    type: TypeItems = None
    children: Optional[List['ItemsOut']]

    class Config:
        orm_mode = True
