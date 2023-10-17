"""
Test cases for YourResourceModel Model

"""
import os
import logging
import unittest
from datetime import datetime
from service import app
from service.models import Shopcart, Item, db, DataValidationError
from tests.factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  Shopcarts   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopcart(unittest.TestCase):
    """Test Cases for Shopcart Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Shopcart.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    # def test_create_shopcart(self):
    #     """It should Create an Shopcart and assert that it exists"""
    #     fake_shopcart = ShopcartFactory()
    #     # pylint: disable=unexpected-keyword-arg
    #     shopcart = Shopcart(
    #         customer_id=fake_shopcart.customer_id,
    #         creation_time=fake_shopcart.creation_time,
    #         last_updated_time=fake_shopcart.last_updated_time,
    #         total_price=fake_shopcart.total_price,
    #     )
    #     self.assertIsNotNone(shopcart)
    #     self.assertEqual(shopcart.id, None)
    #     self.assertEqual(shopcart.customer_id, fake_shopcart.customer_id)
    #     self.assertEqual(shopcart.creation_time, fake_shopcart.creation_time)
    #     self.assertEqual(shopcart.last_updated_time, fake_shopcart.last_updated_time)
    #     self.assertEqual(shopcart.total_price, fake_shopcart.total_price)

    def test_deserialize_missing_key(self):
        missing_key_data = {}
        with self.assertRaises(DataValidationError):
            Shopcart().deserialize(missing_key_data)

    def test_wrong_data_type(self):
        wrong_type_data = {
            "customer_id": "1",
            "creation_time": datetime.now(),
            "last_updated_time": datetime.now(),
            "total_price": 0.0,
        }
        with self.assertRaises(DataValidationError):
            Shopcart().deserialize(wrong_type_data)

    def test_items_deserialization(self):
        data_with_items = {
            "customer_id": 1,
            "creation_time": datetime.now().isoformat(),
            "last_updated_time": datetime.now().isoformat(),
            "total_price": 0.0,
            "items": [
                {
                    "shopcart_id": 1,
                    "name": "food",
                    "price": 0.01,
                    "description": "This is a",
                    "quantity": 0,
                }
            ],
        }

        result = Shopcart().deserialize(data_with_items)
        self.assertEqual(len(result.items), 1)
