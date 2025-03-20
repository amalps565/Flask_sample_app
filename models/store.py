from db import db

class StoreModel(db.Model):
    __tablename__ = "stores"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    tags=db.relationship("TagModel",back_populates="store", lazy="dynamic")
    items=db.relationship("ItemModel",back_populates="store", lazy="dynamic", cascade="all, delete")
    #cascade="all, delete-orphan" means that if we delete a store, it's gonna delete all the items that are related to that store.
    #lazy="dynamic" means that this is not gonna return a list of items, it's gonna return a query builder that has the ability to look into the items table and retrieve the items that are related to this store.
    #Lazy, equal dynamic just means that the items here are not going to be fetched from the database
    # until we tell it to.It's not gonna prefetch them.
    