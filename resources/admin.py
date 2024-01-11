import os
import json
import datetime
import uuid
from passlib.hash import pbkdf2_sha256
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from werkzeug.utils import secure_filename
from sqlalchemy import and_
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db

blp = Blueprint("admin", __name__, description="Show, add, delete users. Change roles")

from schemas import (
    RegisterSchema,
    SuperAdminUserSchema,
    SuperAdminRoleSchema,
    SuperAdminPasswordSchema,
    SuperAdminUsernameSchema,
)
from models import UserModel


@blp.route("/users/users")
class UsersList(MethodView):
    @jwt_required()
    @blp.response(200, RegisterSchema(many=True))
    def get(self):
        admin_uuid = get_jwt_identity()
        if check_admin(admin_uuid):
            users = []
            for user in UserModel.query.all():
                if user.role.role == "user":
                    users.append(user)
            return users
        else:
            abort(409, "You can not access here!")


@blp.route("/users/user/<string:username_uuid>")
class Admin(MethodView):
    @jwt_required()
    @blp.response(200, SuperAdminUserSchema)
    def get(self, username_uuid):
        admin_uuid = get_jwt_identity()
        if check_admin(admin_uuid):
            user = UserModel.query.filter_by(username_uuid=username_uuid).first()
            return user
        else:
            abort(409, message="You can not access here!")


@blp.route("/users/user/<string:username_uuid>/changeRole")
class AdminRole(MethodView):
    @jwt_required()
    @blp.arguments(SuperAdminRoleSchema)
    @blp.response(201, SuperAdminUserSchema)
    def put(self, role_data, username_uuid):
        admin_uuid = get_jwt_identity()
        if check_admin(admin_uuid):
            user = UserModel.query.filter_by(username_uuid=username_uuid).first()
            user.role.role = role_data["role"]
            try:
                db.session.add(user)
                db.session.commit()
            except:
                abort(500, message="Some error has been ...")
            return user
        else:
            abort(409, message="You can not access here!")


@blp.route("/users/user/<string:username_uuid>/changeUsername")
class AdminUsername(MethodView):
    @jwt_required()
    @blp.arguments(SuperAdminUsernameSchema)
    @blp.response(201, SuperAdminUserSchema)
    def put(self, username_data, username_uuid):
        admin_uuid = get_jwt_identity()
        if check_admin(admin_uuid):
            user = UserModel.query.filter_by(username_uuid=username_uuid).first()
            user.username = username_data["username"]
            try:
                db.session.add(user)
                db.session.commit()
            except:
                abort(500, message="Some error has been ...")
            return user
        else:
            abort(409, message="You can not access here!")


@blp.route("/users/user/<string:username_uuid>/changePassword")
class AdminUsername(MethodView):
    @jwt_required()
    @blp.arguments(SuperAdminPasswordSchema)
    @blp.response(201, SuperAdminUserSchema)
    def put(self, password_data, username_uuid):
        admin_uuid = get_jwt_identity()
        if check_admin(admin_uuid):
            user = UserModel.query.filter_by(username_uuid=username_uuid).first()
            user.password = pbkdf2_sha256.hash(password_data["password"])
            try:
                db.session.add(user)
                db.session.commit()
            except:
                abort(500, message="Some error has been ...")
            return user
        else:
            abort(409, message="You can not access here!")


def check_admin(uuid):
    user = UserModel.query.filter_by(username_uuid=uuid).first()
    if user.role.role == "admin":
        return True
    else:
        return False
