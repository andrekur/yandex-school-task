import random
from datetime import datetime as dt
from datetime import timedelta
import unittest
import copy
import uuid

from .base import BaseAPITest
from .tools import generate_imports
from db.schemas import TypeItems

from fastapi import status


class ProductTest(BaseAPITest):
    def test_create_one_product(self):
        data = generate_imports(0, 1)

        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_uncorect_product(self):
        # price =0, is None
        data = generate_imports(count_product=1)
        data['items'][0]['price'] = 0
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data['items'][0]['price'] = None
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # parent uncorect
        data['items'][0]['price'] = 12
        data['items'][0]['parentId'] = str(uuid.uuid4())
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # type not a OFFER
        data['items'][0]['type'] = TypeItems.category
        data['items'][0]['parentId'] = None
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # add with parent
    def test_create_with_parent(self):
        data = generate_imports(count_category=1, count_product=1)
        parent_uuid = [item['id'] for item in data['items'] if item['type'] == TypeItems.category].pop()

        for item in data['items']:
            if item['type'] == TypeItems.product:
                item['parentId'] = parent_uuid

        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CategoryTest(BaseAPITest):
    def test_create_one_category(self):
        data = generate_imports(count_category=1)

        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_uncorect_category(self):
        # price = int, is not None
        data = generate_imports(count_category=1)
        data['items'][0]['price'] = 0
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = generate_imports(count_category=1)
        data['items'][0]['price'] = 12332
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # parent uncorect
        data['items'][0]['price'] = None
        data['items'][0]['parentId'] = str(uuid.uuid4())
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # type not a OFFER
        data['items'][0]['type'] = TypeItems.product
        data['items'][0]['parentId'] = None
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_relation_categories(self):
        data = generate_imports(count_category=3)
        id1 = data['items'][0]['id']
        id2 = data['items'][1]['id']
        id3 = data['items'][2]['id']

        data['items'][2]['parentId'] = id2
        data['items'][1]['parentId'] = id1

        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_relation_categories_and_product(self):
        data = generate_imports(count_category=3)
        products = generate_imports(count_product=2)['items']
        id1 = data['items'][0]['id']
        id2 = data['items'][1]['id']
        id3 = data['items'][2]['id']

        for product in products:
            product['parentId'] = id3

        data['items'][2]['parentId'] = id2
        data['items'][1]['parentId'] = id1

        items = [products[0], ] + data['items'] + [products[1], ]

        data['items'] = items

        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)





