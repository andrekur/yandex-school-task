from itertools import groupby

from .models import ProductModel, CategoryModel, CategoriesRelationsModel
from . import schemas
from fastapi import HTTPException, status

from sqlalchemy import and_


def create_or_upd_product(item_dict, db):
    product = ProductModel(**item_dict)

    if check_product_in_db(item_dict['id'], db):
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
    check_relation_in_db(item_dict['id'], parent, db)

    if check_relation_in_db(item_dict['id'], parent, db):
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


def check_product_in_db(id_product, db):
    product_in_db = db.query(ProductModel).filter(ProductModel.id == id_product).exists()
    return db.query(product_in_db).scalar()


def check_category_in_db(id_category, db):
    category_in_db = db.query(CategoryModel).filter(CategoryModel.id == id_category).exists()
    return db.query(category_in_db).scalar()


def check_relation_in_db(children_id, parent_id, db):
    relation_in_db = db.query(CategoriesRelationsModel).filter(
            CategoriesRelationsModel.children_id == children_id,
            and_(
                CategoriesRelationsModel.parent_id == parent_id
            )
    ).exists()

    return db.query(relation_in_db).scalar()


def get_item_or_exception(item_id, db):
    if check_category_in_db(item_id, db):
        return db.query(CategoryModel).filter(CategoryModel.id == item_id).first()
    elif check_product_in_db(item_id, db):
        return db.query(ProductModel).filter(ProductModel.id == item_id).first()
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')


def get_all_relations(item_id, db):
    relations = set((item.children_id, item.parent_id) for item in db.query(CategoriesRelationsModel).all())
    return get_relation_recursion(item_id, relations)


def get_relation_recursion(item_id, relations):
    arr = [item_id]

    # get all children where item_id is parent
    children_relations = [item[0] for item in relations if item[1] == item_id]

    if len(children_relations) == 0:
        return arr

    for children in children_relations:
        arr += get_relation_recursion(children, relations)

    return arr


def get_relation_item_recursion(item_id, relations, db):
    products = db.query(ProductModel).filter(ProductModel.parentId == item_id)

    category = schemas.ItemsOut.from_orm(get_item_or_exception(item_id, db))
    category.type = schemas.TypeItems.category
    category.children = []

    for product in products:
        product.type = schemas.TypeItems.product
        category.children.append(product)
    del products

    # get all children where item_id is parent
    children_relations = [item[0] for item in relations if item[1] == item_id]

    if len(children_relations) == 0:
        category.price = calc_average(category.children)
        return category

    for children in children_relations:
        category.children.append(get_relation_item_recursion(children, relations, db))

    category.price = calc_average(category.children)
    return category


def calc_average(items):
    if len(items) == 0:
        return None
    return sum(0 if item.price is None else item.price for item in items) // len(items)

