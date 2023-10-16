"""
TestShopCart API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from service import app
from service.models import db, Shopcart, init_db
from service.common import status  # HTTP Status Codes
from tests.factories import ShopcartFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/shopcarts"

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopcartServer(TestCase):
    """Shopcart Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  S H O P C A R T  T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_read_item(self):
        sample_shopcart = Shopcart(customer_id=10, total_price=10)
        db.session.add(sample_shopcart)
        db.session.commit()

        sample_item = Item(
            name="TestItem",
            price=10.99,
            description="Sample Item",
            quantity=5,
            shopcart_id=sample_shopcart.id,
        )
        db.session.add(sample_item)
        db.session.commit()

        # Use the test client to make requests to the api
        response = self.client.get(f"/items/{sample_item.id}")
        data = response.get_json()

        # Check that the response data matches the sample item
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], "TestItem")
        self.assertEqual(data["price"], 10.99)
        self.assertEqual(data["description"], "Sample Item")
        self.assertEqual(data["quantity"], 5)

        # Check a non-existing item
        response = self.client.get("/items/9999")
        self.assertEqual(response.status_code, 404)

    def test_update_item(self):
        # Create a sample item and shopcart
        sample_shopcart = Shopcart(customer_id=10, total_price=10)
        db.session.add(sample_shopcart)
        db.session.commit()

        sample_item = Item(
            name="TestItem",
            price=10.99,
            description="Sample Item",
            quantity=5,
            shopcart_id=sample_shopcart.id,
        )
        db.session.add(sample_item)
        db.session.commit()

        # Update the item
        new_data = {
            "shopcart_id": sample_item.id,
            "name": "UpdatedItem",
            "price": 7.99,
            "description": "Updated Description",
            "quantity": 15,
        }
        response = self.client.put(f"/items/{sample_item.id}", json=new_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_data = response.get_json()

        self.assertEqual(updated_data["name"], "UpdatedItem")
        self.assertEqual(updated_data["price"], 7.99)
        self.assertEqual(updated_data["description"], "Updated Description")
        self.assertEqual(updated_data["quantity"], 15)

    def test_create_shopcart(self):
        """It should Create a new Shopcart"""
        shopcart = ShopcartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_shopcart = resp.get_json()
        print(new_shopcart)
        self.assertEqual(
            new_shopcart["customer_id"],
            shopcart.customer_id,
            "Customer Id does not match",
        )
        self.assertEqual(
            new_shopcart["total_price"],
            shopcart.total_price,
            "Total price does not match",
        )
        self.assertEqual(new_shopcart["items"], shopcart.items, "Items don't not match")
