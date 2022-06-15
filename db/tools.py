from itertools import groupby

from .models import ProductModel, CategoryModel, CategoriesRelationsModel
from . import schemas
from fastapi import HTTPException, status

from sqlalchemy import and_


def create_or_upd_product(item_dict, db):
    product = ProductModel(**item_dict)

    product_in_db = db.query(ProductModel).filter(ProductModel.id == item_dict['id']).exists()
    if db.query(product_in_db).scalar():
        db.query(ProductModel).filter(ProductModel.id == item_dict['id']).update(item_dict)
    else:
        db.add(product)
    db.commit()


def create_or_upd_category(item_dict, db):
    category = CategoryModel(**item_dict)

    category_in_db = db.query(CategoryModel).filter(CategoryModel.id == item_dict['id']).exists()
    if db.query(category_in_db).scalar():
        db.query(CategoryModel).filter(CategoryModel.id == item_dict['id']).update(item_dict)
    else:
        db.add(category)
    db.commit()


def create_or_upd_relation_category(item_dict, parent, db):
    relation_in_db = db.query(CategoriesRelationsModel).filter(
            CategoriesRelationsModel.children_id == item_dict['id'],
            and_(
                CategoriesRelationsModel.parent_id == parent
            )
    ).exists()

    if db.query(relation_in_db).scalar():
        db.query(CategoriesRelationsModel).filter(
            CategoriesRelationsModel.children_id == item_dict['id'],
            and_(
                CategoriesRelationsModel.parent_id == parent
            )).update(
            {
                'children_id': item_dict['id'],
                'parent_id': parent
            }
        )
    else:
        category_relations = CategoriesRelationsModel(children_id=item_dict['id'], parent_id=parent)
        db.add(category_relations)
    db.commit()


def validation_change_type(items, db):
    relations = [(element.id, element.type) for element in items.items]

    for key, group in groupby(relations, lambda x: x[1]):
        group = list(map(lambda x: str(x[0]), group))
        if key == schemas.TypeItems.category:
            product = db.query(ProductModel).filter(ProductModel.id.in_(group)).exists()
            if db.query(product).scalar():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Validation failed')
        else:
            category = db.query(CategoryModel).filter(CategoryModel.id.in_(group)).exists()
            if db.query(category).scalar():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Validation failed')


def validation_parent_in_req(items, db):
    parent_ids_in_db = set(map(lambda x: x[0], db.query(CategoryModel.id).all()))
    parent_ids_in_req = set(item.parentId for item in items.items if item.parentId is not None)
    parent_ids_out_db = parent_ids_in_req - parent_ids_in_db

    item_ids_in_req = set(item.id for item in items.items)
    unknown_parent_ids = parent_ids_out_db - item_ids_in_req
    if len(unknown_parent_ids) != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Validation failed')

    return parent_ids_out_db