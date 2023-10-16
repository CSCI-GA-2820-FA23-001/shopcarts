"""
My Service

Describe what your service does here
GET /shopcarts/{id} - Returns the Shopcart with a given id number
"""

from service.common import status  # HTTP Status Codes
from service.models import Shopcart, Item
from flask import jsonify, request, url_for, abort, make_response

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...


@app.route("/shopcarts/<int:old_cart_id>/items", methods=["POST"])
def create_items(old_cart_id):
    """
    Creates a Item
    This endpoint will create an item based the data in the body that is posted
    """
    app.logger.info("Request to create an Item")
    check_content_type("application/json")
    # Create the shopcart

    newitem = Item()
    newitem.deserialize(request.get_json())
    newitem.create()
    # Create a message to return
    message = newitem.serialize()
    location_url = url_for(
        "read_item", cart_id=old_cart_id, item_id=newitem.id, _external=True
    )

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# UPDATE AN EXISTING ITEM
######################################################################
@app.route("/shopcarts/<int:cart_id>/items/<int:item_id>", methods=["PUT"])
def update_item(cart_id, item_id):
    """
    Update a Item

    This endpoint will update a Item based the id that is posted
    """
    app.logger.info("Request to update item with id: %s", item_id)
    check_content_type("application/json")
    if type(item_id) != int:
        raise TypeError("item_id should be int")

    cart = Shopcart.find(cart_id)
    if not cart:
        abort(status.HTTP_404_NOT_FOUND, f"Cart with id '{cart_id}' was not found.")
    item = Item.find(item_id)

    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")
    item.deserialize(request.get_json())

    item.id = item_id
    item.update()

    app.logger.info("Item with ID [%s] updated.", item.id)
    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# READ A ITEM
######################################################################
@app.route("/shopcarts/<int:cart_id>/items/<int:item_id>", methods=["GET"])
def read_item(cart_id, item_id):
    """
    Retrieve a single item

    This endpoint will return a Pet based on it's id
    """

    app.logger.info("Request for item with id: %s", item_id)

    if type(item_id) != int:
        raise TypeError("item_id should be int")
    cart = Shopcart.find(cart_id)
    if not cart:
        abort(status.HTTP_404_NOT_FOUND, f"Cart with id '{cart_id}' was not found.")

    item = Item.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

    app.logger.info("Returning item: %s", item.name)
    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW SHOPCART
######################################################################


@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Creates a Shopcart
    This endpoint will create an Shopcart based the data in the body that is posted
    """
    app.logger.info("Request to create an Shopcart")
    check_content_type("application/json")
    # Create the shopcart
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    shopcart.create()
    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for("create_shopcarts", shopcart_id=shopcart.id, _external=True)

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
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
# RETRIEVE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a single Shopcart

    This endpoint will return a Shopcart based on it's id
    """
    app.logger.info("Request for shopcart with id: %s", shopcart_id)
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    app.logger.info("Returning shopcart_id: %s", shopcart.id)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# LIST ITEMS IN A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_items(shopcart_id, item_id):
    """
    Return all of the items in a Shopcart

    This endpoint will return a list of items based on shopcart's id
    """
    app.logger.info("Request for item list of the shopcart with id: %s", shopcart_id)
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Item list for Shopcart with id '{shopcart_id}' was not found.",
        )
    items = shopcart.items
    results = [item.serialize() for item in items]

    app.logger.info("Returning item list with shopcart_id: %s", shopcart.id)
    return jsonify(results), status.HTTP_200_OK
