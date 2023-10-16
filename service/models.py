"""
Models for YourResourceModel

All of the models are stored in this module
"""
import logging
from abc import abstractmethod
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    Shopcart.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""

    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""

    def create(self):
        """Creates a ShopCart to the database"""
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Updates a ShopCart to the database"""
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """Removes a ShopCart from the data store"""
        logger.info("Deleting an ShopCart %d", self.id)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


class Shopcart(db.Model, PersistentBase):
    """
    Class that represents a Shopping Cart
    """

    __tablename__ = "shopcart"
    # Table Schema
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer)
    creation_time = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    last_updated_time = db.Column(db.DateTime(), nullable=False, default=datetime.now())
    items = db.relationship("Item", backref="shopcart", passive_deletes=True)
    total_price = db.Column(db.Float(4))

    def __repr__(self):
        return f"<ShopCart from {self.customer_id} id=[{self.id}]>"

    def serialize(self):
        """Serializes a Shopping Cart into a dictionary"""
        shopcart = {
            "id": self.id,
            "customer_id": self.customer_id,
            "creation_time": self.creation_time.isoformat(),
            "last_updated_time": self.last_updated_time.isoformat(),
            "items": [],
            "total_price": self.total_price,
        }

        for item in self.items:
            shopcart["items"].append(item.serialize())

        return shopcart

    def deserialize(self, data):
        """
        Deserializes a Shopping Cart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.creation_time = datetime.fromisoformat(data["creation_time"])
            self.last_updated_time = datetime.fromisoformat(data["last_updated_time"])
            self.total_price = data["total_price"]
            # handle inner list of items
            item_list = data.get("items")
            for json_item in item_list:
                item = Item()
                item.deserialize(json_item)
                self.items.append(item)

        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopping Cart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopping Cart: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self


######################################################################
#  I T E M   M O D E L
######################################################################
class Item(db.Model, PersistentBase):
    """
    Class that represents an Item in a Shopping Cart
    """

    __tablename__ = "item"
    # Table Schema
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shopcart_id = db.Column(
        db.Integer, db.ForeignKey("shopcart.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(64))
    price = db.Column(db.Float(4))
    description = db.Column(db.String(128))
    quantity = db.Column(db.Integer)

    def __repr__(self):
        return f"<Item {self.name} id=[{self.id}] shopcart[{self.shopcart_id}]>"

    def serialize(self) -> dict:
        """Converts an Item into a dictionary"""
        return {
            "id": self.id,
            "shopcart_id": self.shopcart_id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "quantity": self.quantity,
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates an Item from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.shopcart_id = data["shopcart_id"]
            self.name = data["name"]
            self.price = data["price"]
            self.description = data["description"]
            self.quantity = data["quantity"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Item: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Item: body of request contained "
                "bad or no data " + error.args[0]
            ) from error
        return self
