import random
import uuid
from datetime import datetime as dt

from db.schemas import TypeItems


def _generate_category():
    name_size = 12

    category = {
        'id': str(uuid.uuid4()),
        'name': _generate_name(name_size),
        'parentId': None,
        'price': None,
        'type': TypeItems.category
    }

    return category


def _generate_categories(count):
    return [_generate_category() for _ in range(count)]


def generate_imports(count_category=0, count_product=0):
    result = {
        'items':
            _generate_categories(count_category)
            + _generate_products(count_product),
        'updateDate': dt.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    }

    return result


def _generate_product():
    name_size = 12

    category = {
        'id': str(uuid.uuid4()),
        'name': _generate_name(name_size),
        'parentId': None,
        'price': random.randint(1, 10000),
        'type': TypeItems.product
    }

    return category


def _generate_products(count):
    return [_generate_product() for _ in range(count)]


def _generate_name(size):
    return ''.join([chr(random.randint(65, 80)) for _ in range(size)])
