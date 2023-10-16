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
from service.models import db, Shopcart, init_db, Item
from service.common import status  # HTTP Status Codes
from tests.factories import ShopcartFactory, ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/shopcarts"


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

    def _create_shopcarts(self, count):
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for _ in range(count):
            test_shopcart = ShopcartFactory()
            response = self.client.post(BASE_URL, json=test_shopcart.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test shopcart",
            )
            new_shopcart = response.get_json()
            test_shopcart.id = new_shopcart["id"]
            shopcarts.append(test_shopcart)
        return shopcarts

    def _create_items(self, count, shop_cart_id):
        """Factory method to create items in bulk"""
        items = []
        for _ in range(count):
            test_item = ItemFactory(shopcart_id=shop_cart_id)
            response = self.client.post(
                f"{BASE_URL}/{shop_cart_id}/items", json=test_item.serialize()
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test item",
            )
            new_item = response.get_json()
            test_item.id = new_item["id"]
            items.append(test_item)
        return items

    ######################################################################
    #  S H O P C A R T  T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_read_item(self):
        """Get a Item"""
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = self._create_items(1, test_shopcart.id)[0]

        response = self.client.get(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(
            data["shopcart_id"], test_item.shopcart_id, "shopcart_id does not match"
        )
        self.assertEqual(data["price"], test_item.price, "Price does not match")

    def test_update_item(self):
        """
        Update a item

        This endpoint will update a item based the body that is posted
        """

        # create a pet to update
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = ItemFactory(shopcart_id=test_shopcart.id)
        response = self.client.post(
            f"{BASE_URL}/{test_shopcart.id}/items", json=test_item.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the item
        new_item = response.get_json()
        logging.debug(new_item)
        new_item["name"] = "updated_name"
        # a new_item post wait for complete
        response = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}/items/{new_item['id']}", json=new_item
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_item = response.get_json()
        self.assertEqual(updated_item["name"], "updated_name")

    def test_create_item(self):
        """It should create an Item"""
        # create a pet to update
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = ItemFactory(shopcart_id=test_shopcart.id)
        response = self.client.post(
            f"{BASE_URL}/{test_shopcart.id}/items", json=test_item.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_item(self):
        """It should Delete an Item"""
        # create a pet to update
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = ItemFactory(shopcart_id=test_shopcart.id)
        response = self.client.post(
            f"{BASE_URL}/{test_shopcart.id}/items", json=test_item.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.get_json()
        logging.debug(data)
        item_id = data["id"]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{test_shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back and make sure item is not there
        resp = self.client.get(
            f"{BASE_URL}/{test_shopcart.id}/items/{item_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_get_shopcart(self):
        """It should Get a single Shopcart"""
        # get the id of a shopcart
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_shopcart.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(
            data["customer_id"], test_shopcart.customer_id, "Customer Id does not match"
        )
        self.assertEqual(
            data["total_price"], test_shopcart.total_price, "Total price does not match"
        )

    def test_get_shopcart_not_found(self):
        """It should not Get a Shopcart thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_list_shopcarts(self):
        """It should List all shopcarts"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self._create_shopcarts(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_item_list(self):
        """It should Get a list of Items"""
        test_shopcart = self._create_shopcarts(1)[0]
        self._create_items(5, test_shopcart.id)

        response = self.client.get(f"{BASE_URL}/{test_shopcart.id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_item_list_not_found(self):
        """It should not Get a list of Items thats not Found"""

        response = self.client.get(f"{BASE_URL}/0/items")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])
