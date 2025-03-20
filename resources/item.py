import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from models import ItemModel

from schemas import ItemSchema,ItemUpdateSchema

from db import db
from sqlalchemy.exc import SQLAlchemyError
# from db import items

blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200,ItemSchema)
    def get(self, item_id):
        return ItemModel.query.get_or_404(item_id)
    
    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
            
        item= ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": f"Item {item_id} deleted."}
    #use argyments decorator to validate the incoming data
    #the item_data must be used in front of the item_id
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200,ItemSchema)
    def put(self,item_data, item_id):
        item=ItemModel.query.get(item_id)
        if item:
            item.name=item_data["name"]
            item.price=item_data["price"]
        else:
            item=ItemModel(id=item_id,**item_data)
        db.session.add(item)
        db.session.commit()
        
        return item
        # item_data = request.get_json()
        # try:
        #     item = items[item_id]

        #     # https://blog.teclado.com/python-dictionary-merge-update-operators/
        #     item |= item_data
        #     return item
        # except KeyError:
        #     abort(404, message="Item not found.")
        


@blp.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200,ItemSchema(many=True))
    def get(self):
        # return {"items": list(items.values())}
        return ItemModel.query.all()
    #the ItemSchema is used to validate the incoming data(JSON)
    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201,ItemSchema)
    def post(self,item_data):
        item_data = request.get_json()
        # for item in items.values():
        #     if (
        #         item_data["name"] == item["name"]
        #         and item_data["store_id"] == item["store_id"]
        #     ):
        #         abort(400, message=f"Item already exists.")

        # item_id = uuid.uuid4().hex
        # item = {**item_data, "id": item_id}
        # items[item_id] = item
        item=ItemModel(**item_data)
        try:
            db.session.add(item)#we can add multiple items to the session
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="Error occured while adding item to the database")

        return item