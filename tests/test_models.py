"""
Test cases for YourResourceModel Model

"""
import os
import logging
import unittest
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

    def test_create_shopcart(self):
        """It should Create an Shopcart and assert that it exists"""
        fake_shopcart = ShopcartFactory()
        # pylint: disable=unexpected-keyword-arg
        shopcart = Shopcart(
            customer_id=fake_shopcart.customer_id,
            creation_time=fake_shopcart.creation_time,
            last_updated_time=fake_shopcart.last_updated_time,
            total_price=fake_shopcart.total_price,
        )
        self.assertIsNotNone(shopcart)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(shopcart.customer_id, fake_shopcart.customer_id)
        self.assertEqual(shopcart.creation_time, fake_shopcart.creation_time)
        self.assertEqual(shopcart.last_updated_time, fake_shopcart.last_updated_time)
        self.assertEqual(shopcart.total_price, fake_shopcart.total_price)

    def test_serialize_an_shopcart(self):
        """It should Serialize an shopcart"""
        shopcart = ShopcartFactory()
        item = ItemFactory()
        shopcart.items.append(item)
        serial_shopcart = shopcart.serialize()
        self.assertEqual(serial_shopcart["id"], shopcart.id)
        self.assertEqual(serial_shopcart["customer_id"], shopcart.customer_id)
        self.assertEqual(
            serial_shopcart["creation_time"], shopcart.creation_time.isoformat()
        )
        self.assertEqual(
            serial_shopcart["last_updated_time"], shopcart.last_updated_time.isoformat()
        )
        self.assertEqual(serial_shopcart["total_price"], shopcart.total_price)
        self.assertEqual(len(serial_shopcart["items"]), 1)
        items = serial_shopcart["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["shopcart_id"], item.shopcart_id)
        self.assertEqual(items[0]["name"], item.name)
        self.assertEqual(items[0]["price"], item.price)
        self.assertEqual(items[0]["description"], item.description)
        self.assertEqual(items[0]["quantity"], item.quantity)

    def test_deserialize_an_shopcart(self):
        """It should Deserialize an shopcart"""
        shopcart = ShopcartFactory()
        shopcart.items.append(ItemFactory())
        shopcart.create()
        shopcart = shopcart.find(shopcart.id)
        serial_shopcart = shopcart.serialize()
        new_shopcart = Shopcart()
        new_shopcart.deserialize(serial_shopcart)
        self.assertEqual(new_shopcart.customer_id, shopcart.customer_id)
        self.assertEqual(new_shopcart.creation_time, shopcart.creation_time)
        self.assertEqual(new_shopcart.last_updated_time, shopcart.last_updated_time)
        self.assertEqual(new_shopcart.total_price, shopcart.total_price)

    def test_deserialize_shopcart_with_key_error(self):
        """It should not Deserialize an shopcart with a KeyError"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, {})

    def test_deserialize_shopcart_with_type_error(self):
        """It should not Deserialize an shopcart with a TypeError"""
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, [])

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an Item with a KeyError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an Item with a TypeError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])


######################################################################
#  Item   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestItems(unittest.TestCase):
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

    def test_create_items(self):
        """It should Create an Item and assert that it exists"""
        fake_shopcart = ShopcartFactory()
        sample_item = ItemFactory(
            shopcart_id=fake_shopcart.id,
            name="TestItem",
            price=10.99,
            description="Sample Item",
            quantity=5,
        )

        self.assertIsNotNone(sample_item)
        self.assertNotEqual(sample_item.id, None)
        self.assertEqual(sample_item.description, "Sample Item")
        self.assertEqual(sample_item.shopcart_id, fake_shopcart.id)
        self.assertEqual(sample_item.price, 10.99)
        self.assertEqual(sample_item.quantity, 5)

    def test_serialize_an_item(self):
        """It should Serialize an Item"""

        fake_shopcart = ShopcartFactory()
        sample_item = ItemFactory(
            shopcart_id=fake_shopcart.id,
            name="TestItem",
            price=10.99,
            description="Sample Item",
            quantity=5,
        )
        # more than one way Serialize, need one for json
        serial_item = sample_item.serialize()

        self.assertEqual(serial_item["id"], sample_item.id)
        self.assertEqual(serial_item["name"], sample_item.name)
        self.assertEqual(serial_item["shopcart_id"], sample_item.shopcart_id)
        self.assertEqual(serial_item["price"], sample_item.price)
        self.assertEqual(serial_item["description"], sample_item.description)

        # more than one way Serialize, need one for string
        self.assertIn(
            str(sample_item),
            f"<Item TestItem id=[{sample_item.id}] shopcart[{fake_shopcart.id}]>",
        )

    def test_deserialize_an_item(self):
        """It should Deserialize an item"""
        fake_shopcart = ShopcartFactory()
        sample_item = ItemFactory(
            shopcart_id=fake_shopcart.id,
            name="TestItem",
            price=10.99,
            description="Sample Item",
            quantity=5,
        )

        serial_item = sample_item.serialize()

        new_item_from_serial = Item()
        new_item_from_serial.deserialize(serial_item)
        # id should not be same cause we were making a new item, just with same name
        self.assertNotEqual(new_item_from_serial.id, sample_item.id)
        self.assertEqual(new_item_from_serial.name, sample_item.name)
        self.assertEqual(new_item_from_serial.price, sample_item.price)
        self.assertEqual(new_item_from_serial.shopcart_id, sample_item.shopcart_id)

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an Item with a KeyError"""
        fake_shopcart = ShopcartFactory()
        sample_item = ItemFactory(shopcart_id=fake_shopcart.id)
        self.assertRaises(DataValidationError, sample_item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an Item with a TypeError"""
        fake_shopcart = ShopcartFactory()
        sample_item = ItemFactory(shopcart_id=fake_shopcart.id)
        self.assertRaises(DataValidationError, sample_item.deserialize, [])
