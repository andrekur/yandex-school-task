from datetime import datetime, timedelta
from typing import Union
from uuid import UUID

from fastapi import Depends, status, Query, HTTPException

from db.schemas import ItemIn, ItemsOut, ProductOut
from db.connector import Session
from db.crud import (
    post_imports,
    del_item,
    get_item_tree,
    get_all_product_by_interval
)

from .api_start import app


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@app.post(
    '/imports',
    status_code=status.HTTP_200_OK,
)
def imports_items(items: ItemIn, db: Session = Depends(get_db)):
    """
    Import new products/categories
    """
    post_imports(db, items)


@app.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK
)
def delete_item(id: UUID, db: Session = Depends(get_db)):
    """
    Delete products/categories by uuid. ondelete=cascade
    """
    del_item(str(id), db)


@app.get(
    '/nodes/{id}',
    status_code=status.HTTP_200_OK,
    response_model=ItemsOut
)
def get_item(id: UUID, db: Session = Depends(get_db)):
    """
    Get product/category by uuid
    """
    return get_item_tree(str(id), db)


@app.get(
    '/sales',
    status_code=status.HTTP_200_OK,
    response_model=ProductOut
)
def get_sales(date: Union[datetime, None] = Query(default=None), db: Session = Depends(get_db)):
    if date is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Bad request')
    return {'items': get_all_product_by_interval(date - timedelta(hours=24), date, db)}
