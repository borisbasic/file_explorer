import os
from datetime import timedelta 
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from db import db

import models
from models import UserModel
from resources.files import blp as FilesBlueprint
from resources.users import blp as UserBlueprint
from resources.super_admin import blp as SuperAdminBlueprint
from resources.admin import blp as AdminBluerprint


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['API_SECRET_KEY']=os.getenv('API_SECRET_KEY')
    app.config['API_TITLE'] = 'PROFILE' 
    app.config['API_VERSION'] = 'v1' 
    app.config['OPENAPI_VERSION'] = '3.0.3' 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    api = Api(app)
    app.config['JWT_SECRET_KEY']=os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager(app)


    with app.app_context():
        db.create_all()
        
        
    @jwt.user_lookup_loader  #GET CURRENT USER
    def user_lookup_callback(jwt_header, jwt_payload):
        username_uuid = jwt_payload['sub']
        return UserModel.query.filter_by(username_uuid=username_uuid).first()
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (jsonify({'description':'Request does not contain an access token', 'error':'authorizatiion_required'}))

    @jwt.invalid_token_loader
    def invalid_token_callbak(error):
        return (jsonify({'message':'Signature verification failed','error':'invalid token'}), 401,)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return(jsonify({'message':'The token has expired', 'error':'token_expired'}), 401,)

    api.register_blueprint(FilesBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(SuperAdminBlueprint)
    api.register_blueprint(AdminBluerprint)
    return app