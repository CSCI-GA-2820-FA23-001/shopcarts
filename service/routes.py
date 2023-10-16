"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort,make_response
from service.common import status  # HTTP Status Codes
from service.models import Shopcart

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
@app.route("/shopcarts",methods=["GET"])
def list_shopcarts():
    """Return all the shopcarts"""
    app.logger.info("Request for shopcarts list")
    shopcarts = []
    shopcarts = Shopcart.all()
    if not shopcarts:
        abort(
            status.HTTP_404_NOT_FOUND,
            "No shopcart found",
        )
    results = [shopcarts.serialize() for shopcart in shopcarts]
    return make_response(jsonify(results),status.HTTP_200_OK)
    
