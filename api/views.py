from typing import List
from fastapi import Depends, status

from db.schemas import ItemIn
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
