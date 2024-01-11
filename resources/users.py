import os
import json
import datetime
import uuid
from passlib.hash import pbkdf2_sha256
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from werkzeug.utils import secure_filename
from sqlalchemy import and_
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required,
    get_jwt_identity,
)
from db import db

blp = Blueprint("user", __name__, description="Register, login, logout methods")

from schemas import (
    RegisterSchema,
    LoginSchema,
    SuperAdminUserSchema,
    SuperAdminRoleSchema,
    SuperAdminPasswordSchema,
    SuperAdminUsernameSchema,
)
from models import UserModel, UserRoleModel


@blp.route("/register")
class Register(MethodView):
    @blp.arguments(RegisterSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(username=user_data["username"]).first()
        if user:
            abort(400, message="User already exists.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
            username_uuid=uuid.uuid4().hex,
        )
        try:
            db.session.add(user)
            db.session.commit()
        except:
            abort(500, message="An error occured while loading data")
        user_role = UserRoleModel(
            role=user_data["role_"], username_uuid=user.username_uuid
        )
        try:
            db.session.add(user_role)
            db.session.commit()
        except:
            abort(500, message="An error occured while loading data")
        return {"message": "You are register successfully!"}


@blp.route("/login")
class Login(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, login_data):
        user = UserModel.query.filter_by(username=login_data["username"]).first()
        if (
            user
            and pbkdf2_sha256.verify(login_data["password"], user.password)
            and user.role.role == "super_admin"
        ):
            access_token = create_access_token(identity=user.username_uuid)
            return {
                "message": "You are logged as super_admin!",
                "access_token": access_token,
            }
        if login_data["username"] == os.getenv("SUPER_ADMIN_USERNAME") and login_data[
            "password"
        ] == os.getenv("SUPER_ADMIN_PASSWORD"):
            user = UserModel(
                username=login_data["username"],
                password=pbkdf2_sha256.hash(login_data["password"]),
                username_uuid=uuid.uuid4().hex,
            )
            try:
                db.session.add(user)
                db.session.commit()
            except:
                abort(500, message="Some error while loading data.")
            user_role = UserRoleModel(
                role="super_admin", username_uuid=user.username_uuid
            )
            try:
                db.session.add(user_role)
                db.session.commit()
            except:
                abort(500, message="Some error while loading data.")
            access_token = create_access_token(identity=user.username_uuid)
            return {
                "message": "You are logged as super_admin",
                "access_token": access_token,
            }

        if (
            user
            and pbkdf2_sha256.verify(login_data["password"], user.password)
            and user.role.role == "admin"
        ):
            access_token = create_access_token(identity=user.username_uuid)
            return {"message": "You are logged as admin!", "access_token": access_token}
        if (
            user
            and pbkdf2_sha256.verify(login_data["password"], user.password)
            and user.role.role == "user"
        ):
            access_token = create_access_token(identity=user.username_uuid)
            return {"message": "You are logged in!", "access_token": access_token}
        else:
            abort(401, message="Try again")


@blp.route("/users")
class UsersList(MethodView):
    @jwt_required()
    @blp.response(200, RegisterSchema(many=True))
    def get(self):
        username_uuid = get_jwt_identity()
        user = UserModel.query.filter_by(username_uuid=username_uuid).first()
        if user.role.role == "user":
            abort(409, message="You dont have permission to access here.")
        all_users = UserModel.query.all()
        return all_users
