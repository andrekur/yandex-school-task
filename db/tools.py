from itertools import groupby


from .models import ProductModel, CategoryModel, CategoriesRelationsModel
from . import schemas
from fastapi import HTTPException, status

from sqlalchemy import and_


def create_or_upd_product(item, date, db):
    """
    Create or upd product
    """
    item = _preparation_product_data(item, date)
    product = ProductModel(**item)

    if is_product_in_db(item['id'], db):
        db.query(ProductModel).filter(
            ProductModel.id == item['id']
        ).update(item)
    else:
        db.add(product)
    if item['parentId'] is not None:
        upd_category_date_for_relations(item['parentId'], date, db)
    db.commit()


def upd_category_date_for_relations(category_id, date, db):
    """
    Update date for all relations category
    """
    relations = set(
        (item.children_id, item.parent_id) for item in db.query(
            CategoriesRelationsModel
        )
        .all()
    )
    all_parents = _get_all_category_parent(category_id, relations)
    db.query(CategoryModel).filter(
        CategoryModel.id.in_(all_parents)
    ).update({'date': date})


def _get_all_category_parent(category_id, relations):
    """
    Get all parent for category
    """
    arr = [category_id]

    # get all parent where category_id is children
    parents_relations = [
        item[1] for item in relations if (
                str(item[0]) == category_id and item[1] is not None)
    ]

    if len(parents_relations) == 0:
        return arr

    for parent in parents_relations:
        arr += _get_all_category_parent(parent, relations)

    return arr


def create_or_upd_category_and_relations(item, date, db):
    """
    Create or upd category in db
    """
    parent = item.parentId
    if parent is not None:
        parent = str(parent)

    item = _preparation_category_data(item, date)
    category = CategoryModel(**item)

    if is_category_in_db(item['id'], db):
        db.query(CategoryModel).filter(
            CategoryModel.id == item['id']
        ).update(item)
    else:
        db.add(category)

    upd_category_date_for_relations(item['id'], date, db)

    db.commit()

    create_or_upd_relation_category(item, parent, db)
    db.commit()


def create_or_upd_relation_category(item, parent, db):
    """
    Create or upd category relations
    """
    is_relation_in_db(item['id'], parent, db)

    if is_relation_in_db(item['id'], parent, db):
        db.query(CategoriesRelationsModel).filter(
            CategoriesRelationsModel.children_id == item['id'],
            and_(
                CategoriesRelationsModel.parent_id == parent
            )).update(
            {
                'children_id': item['id'],
                'parent_id': parent
            }
        )
    else:
        category_relations = CategoriesRelationsModel(
            children_id=item['id'],
            parent_id=parent
        )
        db.add(category_relations)
    db.commit()


def is_product_in_db(product_id, db) -> bool:
    """
    Is product in db ? Yes return True, No return False
    """
    product_in_db = db.query(ProductModel).filter(
        ProductModel.id == product_id
    ).exists()
    return db.query(product_in_db).scalar()


def is_category_in_db(category_id, db) -> bool:
    """
    Is category in db ? Yes return True, No return False
    """
    category_in_db = db.query(CategoryModel).filter(
        CategoryModel.id == category_id
    ).exists()
    return db.query(category_in_db).scalar()


def is_relation_in_db(children_id, parent_id, db) -> bool:
    """
    Is category relation in db ? Yes return True, No return False
    """
    relation_in_db = db.query(CategoriesRelationsModel).filter(
            CategoriesRelationsModel.children_id == children_id,
            and_(
                CategoriesRelationsModel.parent_id == parent_id
            )
    ).exists()

    return db.query(relation_in_db).scalar()


def get_all_category_relations(category_id, db):
    """
    Get all relation for this category
    """
    relations = set(
        (str(item.children_id), str(item.parent_id)) for item in db.query(
            CategoriesRelationsModel
        ).all())
    return _get_all_category_relations(category_id, relations)


def get_item_or_404(item_id, db):
    """
    Search item in db. If item not found raise 404 Not Found, else return item
    """
    if is_category_in_db(item_id, db):
        return db.query(CategoryModel).filter(
            CategoryModel.id == item_id
        ).first()
    elif is_product_in_db(item_id, db):
        return db.query(ProductModel).filter(
            ProductModel.id == item_id
        ).first()
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Item not found'
    )


def build_items_tree(item_id, relations, db):
    """
    Build output thee for item
    """
    products = db.query(ProductModel).filter(ProductModel.parentId == item_id)

    category = schemas.ItemsOut.from_orm(get_item_or_404(item_id, db))
    category.type = schemas.TypeItems.category
    category.children = []

    for product in products:
        product.type = schemas.TypeItems.product
        category.children.append(product)
    del products

    # get all children where item_id is parent
    children_relations = [
        str(item[0]) for item in relations if str(item[1]) == item_id
    ]

    if len(children_relations) == 0:
        # check for one item
        category.price = _calc_average(category)
        return category

    for children in children_relations:
        category.children.append(build_items_tree(children, relations, db))

    # add parentId
    for child in category.children:
        if hasattr(child, 'parentId'):
            child.parentId = category.id

    category.price = _calc_average(category)

    return category


def _calc_average(category):
    """
    Calculation average items
    """
    sum, count = _get_sum_and_count(category)

    if count != 0:
        return sum // count

    return None


def _get_sum_and_count(items):
    """
    Get sum product.price and count product
    """
    if items.children is None:
        return 0, 0
    sum = 0
    count = 0
    for child in items.children:
        if child.type is schemas.TypeItems.product:
            sum += child.price
            count += 1
        else:
            _sum, _count = _get_sum_and_count(child)
            sum += _sum
            count += _count
    return sum, count


def _preparation_product_data(product, date):
    """
    Preparation product to add
    """
    product = product.dict()
    product['id'] = str(product['id'])
    product['date'] = date
    del product['type']

    if product.get('parentId') is not None:
        product['parentId'] = str(product.get('parentId'))
    return product


def _preparation_category_data(category, date):
    """
    Preparation category to add
    """
    category = category.dict()
    category['id'] = str(category['id'])
    category['date'] = date

    del category['parentId']
    del category['type']

    return category


def _get_all_category_relations(category_id, relations):
    """
    Get all relations(where category is parent) for category id
    """
    arr = [category_id]

    # get all children where category_id is parent
    children_relations = [
        item[0] for item in relations if item[1] == category_id
    ]

    if len(children_relations) == 0:
        return arr

    for children in children_relations:
        arr += _get_all_category_relations(children, relations)

    return arr


def validation_change_type(items, db):
    """
    Validation change type item.
    If item.type in request and in bd is different -> raise 400 Bad Request
    """
    relations = [(element.id, element.type) for element in items.items]

    for key, group in groupby(relations, lambda x: x[1]):
        group = list(map(lambda x: str(x[0]), group))
        if key == schemas.TypeItems.category:
            product = db.query(ProductModel).filter(
                ProductModel.id.in_(group)
            ).exists()
            if db.query(product).scalar():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Validation failed'
                )
        else:
            category = db.query(CategoryModel).filter(
                CategoryModel.id.in_(group)
            ).exists()
            if db.query(category).scalar():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Validation failed'
                )


def validation_parent_in_req(items, db):
    """
    Validation item parent in req.
    If type item.parent is product -> raise 400 Bad Request
    """
    parent_ids_in_db = set(
        map(lambda x: x[0], db.query(CategoryModel.id).all())
    )
    parent_ids_in_req = set(
        item.parentId for item in items.items if item.parentId is not None
    )
    parent_ids_out_db = parent_ids_in_req - parent_ids_in_db

    item_ids_in_req = set(item.id for item in items.items)
    unknown_parent_ids = parent_ids_out_db - item_ids_in_req
    if len(unknown_parent_ids) != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Validation failed'
        )

    return parent_ids_out_db
