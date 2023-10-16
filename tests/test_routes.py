"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from service import app
from service.models import ShopCart, Item, db
from service.common import status  # HTTP Status Codes

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestRoute(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False

        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        ShopCart.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.remove()
        db.drop_all()

    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()
        db.session.query(ShopCart).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_read_item(self):
        sample_shopcart = ShopCart(customer_id=0, total_price=10)
        sample_item = Item(
            name="TestItem",
            price=10.99,
            description="Sample Item",
            quantity=5,
            shopcart_id=sample_shopcart.id,
        )
        db.session.add(sample_shopcart, sample_item)
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
        response = self.client.put(
            "/items/<id>",
            json={"name": "item_name", "price": "item_price"},
            content_type="sth to pass not as json",
        )
        status_code = response.status_code
        data = response.data
        jsonfile = response.json

        self.assertEqual(response.status_code, status.HTTP_200_OK)
