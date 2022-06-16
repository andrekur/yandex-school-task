from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import schemas
from .models import CategoryModel, CategoriesRelationsModel, ProductModel
from .tools import (
    create_category,
    create_product,
    validation_change_type,
    validation_parent_in_req,
    get_item_or_404,
    get_all_relations,
    get_relation_item_recursion,
)


def post_imports(db: Session, request_data):
    """
    Insert data in db
    """
    upd_date = request_data.updateDate

    validation_change_type(request_data, db)

    items_dict = {item.id: item for item in request_data.items}
    parent_ids_out_db = validation_parent_in_req(request_data, db)
    for parent_id_out_db in parent_ids_out_db:
        item = items_dict.get(parent_id_out_db)
        if item is None:
            continue
        # product is parent
        if item.type != schemas.TypeItems.category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Validation Failed')
        # item is end point
        if item.parentId is None:
            create_category(item, upd_date, db)
            del items_dict[item.id]
        else:
            _add_category(item.parentId, items_dict, upd_date, db)
            create_category(item, upd_date, db)
            del items_dict[item.id]
    # add remaining items
    for key, val in items_dict.items():
        if val.type == schemas.TypeItems.category:
            create_category(val, upd_date, db)
        else:
            create_product(val, upd_date, db)
    db.commit()


def _add_category(id, items_dict, date, db):
    """
    Recursion add category to insert in db
    """
    item = items_dict.get(id)
    # if parent already enter
    if item is None:
        return
    if item.parentId is None:
        create_category(item, date, db)
        del items_dict[item.id]
    else:
        _add_category(item.parentId, items_dict, date, db)
        create_category(item, date, db)
        del items_dict[item.id]


def del_item(item_id, db):
    item = get_item_or_404(item_id, db)

    # del product
    if hasattr(item, 'parentId'):
        db.query(ProductModel).filter(ProductModel.id == item_id).delete()
        db.commit()
        return
    # item is a category
    # search all relation in graph
    all_children = get_all_relations(item_id, db)
    db.query(CategoryModel).filter(CategoryModel.id.in_(all_children)).delete()

    db.commit()


def get_item(item_id, db):
    item = get_item_or_404(item_id, db)
    # check that item is OFFER
    if hasattr(item, 'parentId'):
        item.type = schemas.TypeItems.product
        return item

    relations = set((item.children_id, item.parent_id) for item in db.query(CategoriesRelationsModel).all())
    return get_relation_item_recursion(item_id, relations, db)
