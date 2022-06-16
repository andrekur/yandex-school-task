
import copy

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .models import CategoryModel, CategoriesRelationsModel

from . import schemas
from .tools import (
    create_or_upd_product,
    create_or_upd_category,
    create_or_upd_relation_category,
    validation_change_type,
    validation_parent_in_req,
    get_item_or_exception,
    get_all_relations,
    get_relation_item_recursion
)


def post_imports(db: Session, items):
    """
    Insert data in db
    """
    upd_date = items.updateDate
    
    validation_change_type(items, db)
    parent_ids_out_db = validation_parent_in_req(items, db)

    items_dict = {item.id: item for item in items.items}

    for parent_id_out_db in parent_ids_out_db:
        item = items_dict.get(parent_id_out_db)
        if item is None:
            continue
        if item.type != schemas.TypeItems.category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Validation Failed')
        if item.parentId is None:
            insert_category(item, upd_date, db)
            del items_dict[item.id]
        else:
            add_category(item.parentId, items_dict, upd_date, db)
            insert_category(item, upd_date, db)
            del items_dict[item.id]

    for key, val in items_dict.items():
        if val.type == schemas.TypeItems.category:
            insert_category(val, upd_date, db)
        else:
            insert_product(val, upd_date, db)
    db.commit()


def add_category(id, items_dict, date, db):
    item = items_dict.get(id)
    # if parent already enter
    if item is None:
        return
    if item.parentId is None:
        insert_category(item, date, db)
        del items_dict[item.id]
    else:
        add_category(item.parentId, items_dict, date, db)
        insert_category(item, date, db)
        del items_dict[item.id]


def insert_product(item, date, db):
    item_dict = item.dict()
    item_dict['id'] = str(item_dict['id'])
    item_dict['date'] = date
    del item_dict['type']

    if item_dict.get('parentId') is not None:
        item_dict['parentId'] = str(item_dict.get('parentId'))

    create_or_upd_product(item_dict, db)


def insert_category(item, date, db):
    item_dict = item.dict()
    item_dict['id'] = str(item_dict['id'])

    parent = copy.copy(item_dict.get('parentId'))
    if parent is not None:
        parent = str(parent)

    del item_dict['parentId']
    del item_dict['type']

    item_dict['date'] = date

    # check in db if True -> UPD else INSERT
    create_or_upd_category(item_dict, db)
    create_or_upd_relation_category(item_dict, parent, db)
    db.commit()


def del_item(item_id, db):
    get_item_or_exception(item_id, db)
    # search all relation in graph
    all_children = get_all_relations(item_id, db)
    db.query(CategoryModel).filter(CategoryModel.id.in_(all_children)).delete()

    db.commit()


def get_item(item_id, db):
    get_item_or_exception(item_id, db)
    relations = set((item.children_id, item.parent_id) for item in db.query(CategoriesRelationsModel).all())
    return get_relation_item_recursion(item_id, relations, db)
