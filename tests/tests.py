import uuid

from fastapi import status

from db.schemas import TypeItems
from .base import BaseAPITest
from .tools import generate_imports


class ProductTest(BaseAPITest):
    def test_create_one_product(self):
        data = generate_imports(count_product=1)

        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.get_items(data['items'][0]['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check get item
        del data['updateDate']
        data['items'][0]['children'] = None
        data = data['items'][0]
        self.assertEqual(response.json(), data)

    def test_create_incorrect_product(self):
        data = generate_imports(count_product=1)

        # check item not in db
        response = self.get_items(data['items'][0]['id'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # price =0
        data['items'][0]['price'] = 0
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # price is None
        data['items'][0]['price'] = None
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # parent incorrect
        data['items'][0]['price'] = 12
        data['items'][0]['parentId'] = str(uuid.uuid4())
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # type not a OFFER
        data['items'][0]['type'] = TypeItems.category
        data['items'][0]['parentId'] = None
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_del_product(self):
        data = generate_imports(count_product=1)

        # create product
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # del product
        response = self.del_items(data['items'][0]['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check del product
        response = self.get_items(data['items'][0]['id'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_product_with_parent(self):
        data = generate_imports(count_category=1, count_product=1)
        parent_uuid = [item['id'] for item in data['items'] if item['type'] == TypeItems.category].pop()

        for item in data['items']:
            if item['type'] == TypeItems.product:
                item['parentId'] = parent_uuid

        # create items
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check get product
        product = [item for item in data['items'] if item['id'] != parent_uuid].pop()
        product['children'] = None

        response = self.get_items(product['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), product)

        # check get category
        category = [item for item in data['items'] if item['id'] == parent_uuid].pop()
        category['children'] = [product, ]
        category['price'] = product['price']

        response = self.get_items(category['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), category)

    def test_del_category_with_product(self):
        data = generate_imports(count_category=1, count_product=1)
        parent_uuid = [item['id'] for item in data['items'] if item['type'] == TypeItems.category].pop()

        for item in data['items']:
            if item['type'] == TypeItems.product:
                item['parentId'] = parent_uuid
        # create items
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # del parent
        response = self.del_items(parent_uuid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check del result
        for item in data['items']:
            response = self.get_items(item['id'])
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CategoryTest(BaseAPITest):
    def test_create_one_category(self):
        data = generate_imports(count_category=1)
        # create category
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check return
        response = self.get_items(data['items'][0]['id'])
        category = data['items'][0]
        category['children'] = []

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), category)

    def test_create_incorrect_category(self):
        # price = 0
        data = generate_imports(count_category=1)
        data['items'][0]['price'] = 0
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # price is int
        data = generate_imports(count_category=1)
        data['items'][0]['price'] = 12332
        response = self.post_imports(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # parent incorrect
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

        # TODO check output

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

        # TODO check output
