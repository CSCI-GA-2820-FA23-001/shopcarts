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
from service.routes import read_item, update_item, delete_items, update_shopcart
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

    def test_index(self):
        """It should call the home page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Shopcarts REST API Service")

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
        # create a item to update
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = ItemFactory(shopcart_id=test_shopcart.id)
        response = self.client.post(
            f"{BASE_URL}/{test_shopcart.id}/items", json=test_item.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_item(self):
        """It should Delete an Item"""
        # create a item to update
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
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

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

    def test_update_shopcart(self):
        """
        Update a shopcart

        This endpoint will update a shopcart based on the body that is posted
        """

        # create a shopcart to update
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the shopcart
        new_shopcart = response.get_json()
        logging.debug(new_shopcart)
        new_shopcart["total_price"] = 99.99
        # a new_shopcart post wait for complete
        response = self.client.put(f"{BASE_URL}/{test_shopcart.id}", json=new_shopcart)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_shopcart = response.get_json()
        self.assertEqual(updated_shopcart["total_price"], 99.99)

    def test_delete_shopcart(self):
        """It should Delete a Shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        response = self.client.delete(f"{BASE_URL}/{shopcart.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_empty_shopcart(self):
        """It should Empty a Shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        self._create_items(5, shopcart.id)
        response = self.client.delete(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_update_item_not_found(self):
        """test if not found error raise"""
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = ItemFactory(shopcart_id=test_shopcart.id)
        response = self.client.post(
            f"{BASE_URL}/{test_shopcart.id}/items", json=test_item.serialize()
        )

        # update the item
        new_item = response.get_json()
        logging.debug(new_item)
        new_item["name"] = "updated_name"

        # not found the cart of item
        response = self.client.put(f"{BASE_URL}/{999}/items/{0}", json=new_item)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("Cart with id '999' was not found.", data["message"])

        # not found the item
        response = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}/items/{9999}", json=new_item
        )
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("Item with id '9999' was not found.", data["message"])

    def test_read_item_not_found(self):
        """test if not found error raise"""

        # not found the cart of item
        response = self.client.get(f"{BASE_URL}/{9999}/items/{0}")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("Cart with id '9999' was not found.", data["message"])

        # not found the item
        test_shopcart = self._create_shopcarts(1)[0]
        # test_item = self._create_items(1, test_shopcart.id)[0]
        response = self.client.get(f"{BASE_URL}/{test_shopcart.id}/items/{999}")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("Item with id '999' was not found.", data["message"])

    def test_get_shopcart_not_found(self):
        """It should not Get a Shopcart thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_read_item_invalid_para(self):
        """test if ValueError raised for bad input"""

        self.assertRaises(TypeError, read_item, cart_id="abc", item_id="bcc")

    def test_delete_items_invalid_para(self):
        """test if ValueError raised for bad input"""

        self.assertRaises(TypeError, delete_items, shopcart_id=0, item_id="bcc")

    def test_update_item_invalid_para(self):
        """test if ValueError raised for bad input when updating item"""
        self.assertRaises(TypeError, update_item, cart_id="abc", item_id="bcc")

    def test_update_shopcart_invalid_para(self):
        """test if ValueError raised for bad input when updating shopcart"""
        self.assertRaises(TypeError, update_shopcart, shopcart_id="abc")

    def test_update_shopcart_not_found(self):
        """test if error aborted for shopcart not exist when updating shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]

        # not found the shopcart
        response = self.client.put(f"{BASE_URL}/0", json=test_shopcart.serialize())
        self.assertEqual(response.status_code, 404)

    def test_update_item_invalid_data(self):
        """It should not update a item with invalid data"""
        # create sample cart and item
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = self._create_items(1, test_shopcart.id)[0]
        response = self.client.post(
            f"{BASE_URL}/{test_shopcart.id}/items", json=test_item.serialize()
        )
        new_item = response.get_json()

        # not provide a json for item serilize
        response = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}", json="abc"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn(
            "Invalid Item: body of request contained bad or no data string indices must be integers, not 'str'",
            data["message"],
        )

        # can not accept no shopcart_id
        del new_item["shopcart_id"]
        response = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}", json=new_item
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Invalid Item: missing shopcart_id", data["message"])

    def test_update_item_non_json_data(self):
        """It should not update a item with non-json data"""
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = self._create_items(1, test_shopcart.id)[0]
        response = self.client.post(
            f"{BASE_URL}/{test_shopcart.id}/items", json=test_item.serialize()
        )

        response = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}",
            content_type="application/css",
        )

        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        data = response.get_json()
        self.assertIn(
            "Content-Type must be application/json",
            data["message"],
        )

    def test_list_shopcarts(self):
        """It should List all shopcarts"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 0)
        self._create_shopcarts(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
    
    def test_query_list_shopcarts(self):
        """It should List shopcarts with query"""
        fake_shopcarts = self._create_shopcarts(3)
        fake_items = self._create_items(1,fake_shopcarts[0].id)
        #test query item id
        response = self.client.get(BASE_URL,query_string=f"item={fake_items[0].id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data),1)
        self.assertEqual(data[0]["id"],fake_items[0].shopcart_id)
        #test query max total price
        response = self.client.get(BASE_URL,query_string=f"maxprice={fake_shopcarts[0].total_price}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data),3)
        #test query min total price 
        response = self.client.get(BASE_URL,query_string=f"minprice={fake_shopcarts[0].total_price}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        #self.assertEqual(len(data),1)
        self.assertEqual(data[0]["id"],fake_shopcarts[0].id)




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
