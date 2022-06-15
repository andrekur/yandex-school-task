from pydantic import BaseModel, UUID4, PositiveInt, constr, validator, conint
from enum import Enum
from typing import List
from datetime import datetime, timezone
from fastapi import HTTPException, status


def convert_datetime_to_iso_8601(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def transform_to_utc_datetime(dt: datetime) -> datetime:
    return dt.astimezone(tz=timezone.utc)


class TypeItems(str, Enum):
    product = 'OFFER'
    category = 'CATEGORY'


class ItemsBase(BaseModel):
    id: UUID4
    name: constr(min_length=1)
    parentId: UUID4 = None
    price: conint(gt=0) = None
    type: TypeItems


class ItemIn(BaseModel):
    items: List[ItemsBase]
    updateDate: datetime

    _normalize_datetime = validator(
        "updateDate",
        allow_reuse=True)(transform_to_utc_datetime)

    class Config:
        json_encoders = {
            datetime: convert_datetime_to_iso_8601
        }
        orm_mode = True

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
