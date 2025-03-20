from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask import jsonify
from flask_migrate import Migrate
import secrets
import os
#models need to be imported before we initialize the SQLAlchemy extension.
#Because SQLalchemy needs to know what tables and columns to create when we tell it to create our tables for us.
from db import db
import models

from blocklist import BLOCKLIST

from resources.item import blp as item_blp
from resources.store import blp as store_blp
from resources.tag import blp as tag_blp
from resources.user import blp as user_blp
def create_app(db_url=None):
    app=Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"]=True
    app.config["API_TITLE"]="Stores rest API"
    app.config["API_VERSION"]="1.0" 
    app.config["OPENAPI_VERSION"]="3.0.2"
    app.config["OPENAPI_URL_PREFIX"]="/" 
    app.config["OPENAPI_SWAGGER_UI_PATH"]="/swagger_ui"
    app.config["OPENAPI_SWAGGER_UI_URL"]="https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    #if database url is not provided then use sqlite
    app.config["SQLALCHEMY_DATABASE_URI"]=db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
    db.init_app(app)
    
    migrate=Migrate(app,db)

    api=Api(app)
    app.config["JWT_SECRET_KEY"]="user"
    # app.config["JWT_SECRET_KEY"]=secrets.SystemRandom().getrandbits(128)
    jwt=JWTManager(app)
    
    # @app.on_first_request
    # def create_tables():
    #     db.create_all()
    
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # TODO: Read from a config file instead of hard-coding
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    # JWT configuration ends here
    
    # with app.app_context():
    #     db.create_all()
    app.register_blueprint(item_blp)
    app.register_blueprint(store_blp)
    app.register_blueprint(tag_blp)
    app.register_blueprint(user_blp)
    
    return app
