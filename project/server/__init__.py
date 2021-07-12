from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from project.server.config import DevelopmentConfig
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_rest_paginate import Pagination

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
CORS(app, origins="*", headers=['Content-Type', 'Authorization'], expose_headers='Authorization')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

from project.server.users.routes import user_blueprint
from project.server.auth.routes import auth_blueprint
from project.server.parcels.routes import parcel_blueprint
from project.server.sender.routes import customer_blueprint
from project.server.receiver.routes import receiver_blueprint

app.register_blueprint(user_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(parcel_blueprint)
app.register_blueprint(customer_blueprint)
app.register_blueprint(receiver_blueprint)

# def create_app(config_class=DevelopmentConfig):
#     app = Flask(__name__)
#     app.config.from_object(DevelopmentConfig)
#     db.init_app(app)
#     bcrypt.init_app(app)
#
#     return app