"""
Shopcarts Service

This microservice is responsible for managing the shopcarts

GET /shopcarts/{id} - Returns the Shopcart with a given id number
POST /shopcarts - creates a new Shopcart record in the database
PUT /shopcarts/{id} - updates a Shopcart record in the database
DELETE /shopcarts/{id} - deletes a Shopcart record in the database
GET /shopcarts - returns a list of Shopcarts from the database
DELETE /shopcarts/{id}/items - empties a Shopcart
GET /shopcarts/{id}/items - returns a list of Items from the database
GET /shopcarts/{id}/items/{id} - returns a list of Items from the database
POST /shopcarts/{id}/items - creates a new Item record in the database
PUT /shopcarts/{id}/items/{id} - updates a Item record in the database
DELETE /shopcarts/{id}/items/{id} - deletes a Item record in the database
GET /shopcarts/{id}/items/{id} - returns a list of Items from the database
"""

from flask import jsonify, request, abort, make_response
from flask_restx import Resource, fields, reqparse

# from jinja2.exceptions import TemplateNotFound
from service.common import status  # HTTP Status Codes
from service.models import Shopcart, Item


# Import Flask application
from . import app, api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


######################################################################
#  K8S HEALTH POINTS
######################################################################


@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


# Define the model so that the docs reflect what can be sent
create_shopcarts_model = api.model(
    "Shopcarts",
    {
        "customer_id": fields.Integer(required=True, description="Customer ID"),
        "total_price": fields.Float(
            required=False,
            description="The total price of the shopcart",
        ),
        "items": fields.List(
            fields.Nested(
                api.model(
                    "Item",
                    {
                        "name": fields.String(
                            required=False, description="Name of the item"
                        ),
                        "quantity": fields.Integer(
                            required=False, description="Quantity of the item"
                        ),
                        "price": fields.Float(
                            required=False, description="Price of the item"
                        ),
                        "description": fields.String(
                            required=False, description="Description of the item"
                        ),
                        "id": fields.Integer(
                            required=False,
                            description="Item ID",
                        ),
                        "shopcart_id": fields.Integer(
                            required=False, description="The shopcart id"
                        ),
                    },
                )
            ),
            required=False,
            description="List of items in the shopcart",
        ),
        "creation_time": fields.DateTime(
            required=False, description="The creation time of the shopcart"
        ),
        "last_updated_time": fields.DateTime(
            required=False, description="The last updated time of the shopcart"
        )
        # pylint: disable=protected-access
    },
)

shopcarts_model = api.inherit(
    "ShopcartsModel",
    create_shopcarts_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# query string arguments
shopcarts_args = reqparse.RequestParser()
shopcarts_args.add_argument(
    "customer_id",
    type=str,
    location="args",
    required=False,
    help="List Shopcarts by customer ID",
)
shopcarts_args.add_argument(
    "date", type=str, location="args", required=False, help="List Shopcarts by date"
)


######################################################################
# U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )


######################################################################
#  PATH: /shopcarts/{id}
######################################################################
@api.route("/shopcarts/<int:shopcart_id>")
@api.param("shopcart_id", "The Shopcart identifier")
class ShopcartsResource(Resource):
    """
    ShopcartsResource class

    Allows the manipulation of a single Shopcart
    GET /shopcarts/{id} - Returns an Shopcart with the id
    PUT /shopcarts/{id} - Update an Shopcart with the id
    DELETE /shopcarts/{id} -  Deletes an Shopcart with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN shopcart
    # ------------------------------------------------------------------
    @api.doc("get_shopcarts")
    @api.response(404, "shopcart not found")
    def get(self, shopcart_id):
        """
        Retrieve a single shopcart

        This endpoint will return an shopcart based on it's id
        """
        app.logger.info("Request for shopcart with id: %s", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )
        app.logger.info("Returning shopcart_id: %s", shopcart.id)
        return shopcart.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING shopcart
    # ------------------------------------------------------------------
    @api.doc("update_shopcart")
    @api.response(404, "shopcart not found")
    @api.response(400, "The posted shopcart data was not valid")
    @api.expect(shopcarts_model)
    @api.marshal_with(shopcarts_model)
    def put(self, shopcart_id):
        """
        Update an Shopcart

        This endpoint will update an Shopcart based the id that is posted
        """
        app.logger.info("Request to update shopcart with id: %s", shopcart_id)
        if not isinstance(shopcart_id, int):
            raise TypeError("shopcart_id should be int when update a shopcart")

        check_content_type("application/json")

        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Cart with id '{shopcart_id}' was not found when updating it.",
            )

        shopcart.deserialize(api.payload)
        shopcart.id = shopcart_id
        shopcart.update()
        app.logger.info("Shopcart with ID [%s] updated.", shopcart.id)

        return shopcart.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN shopcart
    # ------------------------------------------------------------------
    @api.doc("delete_shopcart")
    @api.response(204, "shopcart deleted")
    def delete(self, shopcart_id):
        """
        Deletes an Shopcart
        This endpoint will delete an Shopcart with the ID given.
        """
        app.logger.info(
            "Request to delete an shopcart with shopcart ID %s", shopcart_id
        )

        shopcart = Shopcart.find(shopcart_id)
        if shopcart:
            shopcart.delete()
            app.logger.info("shopcart with id [%s] was deleted", shopcart_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /shopcarts
######################################################################
@api.route("/shopcarts", strict_slashes=False)
class ShopcartsCollection(Resource):
    """Handles all interactions with collections of Shopcarts"""

    # ------------------------------------------------------------------
    # LIST ALL shopcartS
    # ------------------------------------------------------------------
    @api.doc("list_shopcarts")
    @api.expect(shopcarts_args, validate=False)
    # @api.marshal_list_with(shopcarts_model)
    def get(self):
        """Return all the shopcarts"""
        app.logger.info("Request for shopcarts list")
        shopcarts = []
        shopcarts = Shopcart.all()
        if not shopcarts:
            return make_response(jsonify([]), status.HTTP_200_OK)
        results = [shopcart.serialize() for shopcart in shopcarts]
        customer_id = request.args.get("customer_id")
        item_id = request.args.get("item")
        max_price = request.args.get("maxprice")
        min_price = request.args.get("minprice")
        if customer_id:
            results = [
                cart for cart in results if cart["customer_id"] == int(customer_id)
            ]
        if max_price:
            results = [
                cart
                for cart in results
                if cart["total_price"] <= round(float(max_price), 2)
            ]
        if min_price:
            results = [
                cart
                for cart in results
                if cart["total_price"] >= round(float(min_price), 2)
            ]
        if item_id:
            temp = []
            for cart in results:
                for item in cart["items"]:
                    if item["id"] == int(item_id):
                        temp.append(cart)
                        break
            results = temp
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE A NEW SHOPCART
    # ------------------------------------------------------------------
    @api.doc("create_shopcarts")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_shopcarts_model)
    @api.marshal_with(shopcarts_model, code=201)
    def post(self):
        """
        Creates an shopcart
        This endpoint will create an shopcart based the data in the body that is posted
        """
        app.logger.info("Request to create an shopcart")
        check_content_type("application/json")
        shopcart = Shopcart()
        shopcart.deserialize(api.payload)
        shopcart.create()
        message = shopcart.serialize()
        location_url = api.url_for(
            ShopcartsResource, shopcart_id=shopcart.id, _external=True
        )

        app.logger.info("shopcart with ID [%s] created.", shopcart.id)
        return message, status.HTTP_201_CREATED, {"Location": location_url}


create_items_model = api.model(
    "Items",
    {
        "shopcart_id": fields.Integer(required=True, description="Shopcart ID"),
        "name": fields.String(
            required=False,
            description="The name of item",
        ),
        "price": fields.Float(required=False, description="The price of item"),
        "description": fields.String(
            required=False, description="The description of item"
        ),
        "quantity": fields.Integer(required=False, description="The quantity of item")
        # pylint: disable=protected-access
    },
)

items_model = api.inherit(
    "ItemsModel",
    create_items_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)


######################################################################
#  PATH: /shopcarts/<shopcart_id>/items/<item_id>
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>")
@api.param("shopcart_id", "The shopcart identifier")
@api.param("item_id", "The Item identifier")
class ItemsResource(Resource):
    """
    ItemsResource class

    Allows the manipulation of a single Item
    GET /shopcarts/<shopcart_id>/items/<item_id>
    - Returns an Item with the item_id inside Shopcart with shopcart_id
    PUT /shopcarts/<shopcart_id>/items/<item_id>
    - Update an Item with the item_id inside Shopcart with shopcart_id
    DELETE /shopcarts/<shopcart_id>/items/<item_id>
    - Deletes an Item with the item_id inside Shopcart with shopcart_id
    """

    # ------------------------------------------------------------------
    # READ A ITEM
    # ------------------------------------------------------------------
    @api.doc("read_item")
    @api.response(404, "Item not found")
    @api.marshal_with(items_model)
    def get(self, shopcart_id, item_id):
        """
        Get an Item

        This endpoint returns an item based on it's item id inside shopcart with shopcart id
        """
        app.logger.info("Request for item with id: %s", item_id)
        if not isinstance(shopcart_id, int):
            raise TypeError("shopcart_id should be int")

        if not isinstance(item_id, int):
            raise TypeError("item_id should be int")
        cart = Shopcart.find(shopcart_id)
        if not cart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Cart with id '{shopcart_id}' was not found.",
            )

        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

        app.logger.info("Returning item: %s", item.name)

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ITEM
    # ------------------------------------------------------------------
    @api.doc("update_item")
    @api.response(404, "Item not found")
    @api.response(400, "The posted Item data was not valid")
    @api.expect(items_model)
    @api.marshal_with(items_model)
    def put(self, shopcart_id, item_id):
        """
        Update a Item

        This endpoint will update a Item based the id that is posted
        """
        app.logger.info("Request to update item with id: %s", item_id)
        if not isinstance(item_id, int):
            raise TypeError("item_id should be int")

        check_content_type("application/json")

        cart = Shopcart.find(shopcart_id)
        if not cart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Cart with id '{shopcart_id}' was not found.",
            )
        item = Item.find(item_id)

        if not item:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

        item.deserialize(request.get_json())

        item.id = item_id
        item.update()
        cart.total_price = cart.get_total_price()
        cart.update()
        app.logger.info("Item with ID [%s] updated.", item.id)

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_item")
    @api.response(204, "Item deleted")
    def delete(self, shopcart_id, item_id):
        """
        Delete an Item

        This endpoint will delete an Item based the id specified in the path
        """
        app.logger.info(
            "Request to delete Item %s for ShopCart id: %s", item_id, shopcart_id
        )

        if not isinstance(item_id, int):
            raise TypeError("item_id should be int")
        check_content_type("application/json")

        shopcart = Shopcart.find(shopcart_id)
        # if not shopcart:
        #     abort(
        #         status.HTTP_404_NOT_FOUND,
        #         f"Shopcart with id '{shopcart_id}' could not be found.",
        #     )

        # See if the item exists and delete it if it does
        item = Item.find(item_id)
        # if not item:
        #     abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

        if item:
            shopcart.items.remove(item)
            item.delete()

        shopcart.total_price = shopcart.get_total_price()
        shopcart.update()

        app.logger.info("Item with ID [%s] deleted.", item_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /shopcarts/<shopcart_id>/items
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items", strict_slashes=False)
class ItemsCollection(Resource):
    """Handles all interactions with collections of Items"""

    # ------------------------------------------------------------------
    # LIST ALL ITEMS OF AN shopcart
    # ------------------------------------------------------------------
    @api.doc("list_items")
    @api.response(404, "shopcart not found")
    @api.marshal_list_with(items_model)
    def get(self, shopcart_id):
        """
        Return all of the items in a Shopcart

        This endpoint will return a list of items based on shopcart's id
        """
        app.logger.info(
            "Request for item list of the shopcart with id: %s", shopcart_id
        )

        if not isinstance(shopcart_id, int):
            raise ValueError(
                "shopcart_id must be an integer while list items of shopcart"
            )
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Item list for Shopcart with id '{shopcart_id}' was not found.",
            )

        # Get filters from query parameters
        price_filter = request.args.get("price")
        name_filter = request.args.get("name")

        # Apply filters to the items
        filtered_items = shopcart.items

        if price_filter is not None:
            filtered_items = [
                item for item in filtered_items if item.price == float(price_filter)
            ]

        if name_filter is not None:
            filtered_items = [
                item
                for item in filtered_items
                if name_filter.lower() in item.name.lower()
            ]

        # Serialize the filtered items
        results = [item.serialize() for item in filtered_items]

        app.logger.info(
            "Returning filtered item list with shopcart_id: %s", shopcart.id
        )

        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW ITEM TO AN shopcart
    # ------------------------------------------------------------------
    @api.doc("add_item")
    @api.response(400, "The posted data was not valid")
    @api.response(404, "shopcart not found")
    @api.expect(create_items_model)
    @api.marshal_with(items_model, code=201)
    def post(self, shopcart_id):
        """
        Creates a Item
        This endpoint will create an item based the data in the body that is posted
        """
        app.logger.info("Request to create an Item")
        check_content_type("application/json")

        # See if the shopcart exists and abort if it doesn't
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id '{shopcart_id}' could not be found.",
            )

        # Create an item from the json data
        item = Item()
        item.deserialize(request.get_json())
        # Append the item to the shopcart
        shopcart.items.append(item)
        shopcart.total_price = shopcart.get_total_price()
        shopcart.update()

        # Prepare a message to return
        message = item.serialize()
        return message, status.HTTP_201_CREATED

    # ------------------------------------------------------------------
    # EMPTY SHOPCART
    # ------------------------------------------------------------------
    @api.doc("empty_shopcart")
    @api.response(204, "Items deleted")
    def delete(self, shopcart_id):
        """Empties shopcart"""
        app.logger.info("Request for emptying shopcart with id : %s", shopcart_id)
        shopcart = Shopcart.find(shopcart_id)
        if shopcart:
            for item in shopcart.items:
                item.delete()
        shopcart.total_price = 0
        shopcart.update()
        return "", status.HTTP_204_NO_CONTENT
