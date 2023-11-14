"""
My Service

Describe what your service does here
GET /shopcarts/{id} - Returns the Shopcart with a given id number
"""

from flask import jsonify, request, url_for, abort, make_response
# from jinja2.exceptions import TemplateNotFound
from service.common import status  # HTTP Status Codes
from service.models import Shopcart, Item


# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Shopcarts REST API Service",
            version="1.0",
            # paths=url_for("list_recommendations", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# Place your REST API code here ...


######################################################################
# ADD AN ITEM TO A SHOPCART
######################################################################
@app.route("/shopcarts/<int:old_cart_id>/items", methods=["POST"])
def create_items(old_cart_id):
    """
    Creates a Item
    This endpoint will create an item based the data in the body that is posted
    """
    app.logger.info("Request to create an Item")
    check_content_type("application/json")

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(old_cart_id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{old_cart_id}' could not be found.",
        )

    # Create an item from the json data
    item = Item()
    item.deserialize(request.get_json())

    # Append the item to the shopcart
    shopcart.items.append(item)
    shopcart.update()

    # Prepare a message to return
    message = item.serialize()

    return make_response(jsonify(message), status.HTTP_201_CREATED)


######################################################################
# DELETE AN ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_items(shopcart_id, item_id):
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

    # See if the item exists and delete it if it does
    item = Item.find(item_id)
    if item:
        item.delete()

    app.logger.info("Item with ID [%s] deleted.", item.id)

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# UPDATE AN EXISTING SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcart(shopcart_id):
    """
    Update a Shopcart

    This endpoint will update a Shopcart based the id that is posted
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

    shopcart.deserialize(request.get_json())

    shopcart.id = shopcart_id
    shopcart.update()

    app.logger.info("Shopcart with ID [%s] updated.", shopcart.id)
    return jsonify(shopcart.serialize()), status.HTTP_200_OK


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
    if not isinstance(item_id, int):
        raise TypeError("item_id should be int")

    check_content_type("application/json")

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
    if not isinstance(cart_id, int):
        raise TypeError("cart_id should be int")

    if not isinstance(item_id, int):
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
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcart(shopcart_id):
    """Delete a shopcart with ID"""
    app.logger.info("Request for Deleting a shopcart with id : %s", shopcart_id)
    shopcart = Shopcart.find(shopcart_id)
    if shopcart:
        shopcart.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# EMPTY SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["DELETE"])
def empty_shopcart(shopcart_id):
    """Empties shopcart"""
    app.logger.info("Request for emptying shopcart with id : %s", shopcart_id)
    shopcart = Shopcart.find(shopcart_id)
    if shopcart:
        for item in shopcart.items:
            item.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# LIST ITEMS IN A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_items(shopcart_id):
    """
    Return all of the items in a Shopcart

    This endpoint will return a list of items based on shopcart's id
    """
    app.logger.info("Request for item list of the shopcart with id: %s", shopcart_id)

    if not isinstance(shopcart_id, int):
        raise ValueError("shopcart_id must be an integer while list items of shopcart")
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


######################################################################
# LIST SHOPCARTS
######################################################################


@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """Return all the shopcarts"""
    app.logger.info("Request for shopcarts list")
    shopcarts = []
    shopcarts = Shopcart.all()
    if not shopcarts:
        return make_response(jsonify([]), status.HTTP_200_OK)
    results = [shopcart.serialize() for shopcart in shopcarts]
    item_id = request.args.get("item")
    max_price = request.args.get("maxprice")
    min_price = request.args.get("minprice")

    if max_price:
        results = [
            cart for cart in results if cart["total_price"] <= float(max_price)
        ]
    if min_price:
        results = [
            cart for cart in results if cart["total_price"] >= float(min_price)
        ]
    if item_id:
        temp = []
        for cart in results:
            for item in cart["items"]:
                if item["id"] == int(item_id):
                    temp.append(cart)
                    break
        results = temp
    return make_response(jsonify(results), status.HTTP_200_OK)
