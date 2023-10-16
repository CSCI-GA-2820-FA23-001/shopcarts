"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
from service.common import status  # HTTP Status Codes
from service.models import ShopCart, Item, db

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


@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(id):
    return "sth"


@app.route("/items/<int:item_id>", methods=["GET"])
def read_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return make_response(jsonify(message="Item not found"), 404)
    return jsonify(item.serialize())
