from typing import List
from fastapi import Depends, status

from db.schemas import ItemIn, ItemIdIn, ItemsOut
from db.connector import Session
from db import crud

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
    crud.post_imports(db, items)
    return []


@app.delete(
    '/delete/{id}',
    status_code=status.HTTP_200_OK
)
def delete_item(id: str, db: Session = Depends(get_db)):
    crud.del_item(ItemIdIn(id=id).id, db)


@app.get(
    '/nodes/{id}',
    status_code=status.HTTP_200_OK,
    response_model=ItemsOut
)
def get_item(id: str, db: Session = Depends(get_db)):
    result = crud.get_item(ItemIdIn(id=id).id, db)
    print(result)
    return result
