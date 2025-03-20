from db import db

class TagModel(db.Model):
    __tablename__ = "tags"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False)
    
    store=db.relationship("StoreModel",back_populates="tags")
    items=db.relationship("ItemModel",back_populates="tags",secondary="item_tags")
    #This is a one-to-many relationship, so we're gonna use the back_populates argument in both models.