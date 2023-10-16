"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
from service.common import status  # HTTP Status Codes
from service.models import Shopcart, Item, db

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


######################################################################
# UPDATE AN EXISTING ITEM
######################################################################
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """
    Update a Item

    This endpoint will update a Item based the id that is posted
    """
    app.logger.info("Request to update item with id: %s", item_id)
    check_content_type("application/json")

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
@app.route("/items/<int:item_id>", methods=["GET"])
def read_item(item_id):
    """
    Retrieve a single item

    This endpoint will return a Pet based on it's id
    """

    app.logger.info("Request for item with id: %s", item_id)
    item = Item.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

    app.logger.info("Returning item: %s", item.name)
    return jsonify(item.serialize()), status.HTTP_200_OK


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
