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

blp = Blueprint(
    "super_admin",
    __name__,
    description="Show, add, delete admins and users. Change roles",
)

from schemas import (
    RegisterSchema,
    SuperAdminUserSchema,
    SuperAdminRoleSchema,
    SuperAdminPasswordSchema,
    SuperAdminUsernameSchema,
    SuperAdminSuperAdminSchema,
)
from models import UserModel


@blp.route("/users/admins")
class SuperAdminList(MethodView):
    @jwt_required()
    @blp.response(200, RegisterSchema(many=True))
    def get(self):
        super_admin_uuid = get_jwt_identity()
        if check_super_admin(super_admin_uuid):
            admins = []
            for admin in UserModel.query.all():
                if admin.role.role == "admin":
                    admins.append(admin)
            return admins
        else:
            abort(409, "You can not access here!")


@blp.route("/users/admin/<string:username_uuid>")
class SuperAdmin(MethodView):
    @jwt_required()
    @blp.response(200, SuperAdminUserSchema)
    def get(self, username_uuid):
        super_admin_uuid = get_jwt_identity()
        if check_super_admin(super_admin_uuid):
            user = UserModel.query.filter_by(username_uuid=username_uuid).first()
            return user
        else:
            abort(409, message="You can not access here!")

    @jwt_required()
    def delete(self, username_uuid):
        super_admin_uuid = get_jwt_identity()
        if check_super_admin(super_admin_uuid):
            user = UserModel.query.filter_by(username_uuid=username_uuid).first()
            db.session.delete(user)
            db.session.commit()
        return {"message": "User is deleted!"}


@blp.route("/users/admin/<string:username_uuid>/changeRole")
class SuperAdminRole(MethodView):
    @jwt_required()
    @blp.arguments(SuperAdminRoleSchema)
    @blp.response(201, SuperAdminUserSchema)
    def put(self, role_data, username_uuid):
        super_admin_uuid = get_jwt_identity()
        if check_super_admin(super_admin_uuid):
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


@blp.route("/users/admin/<string:username_uuid>/changeUsername")
class SuperAdminUsername(MethodView):
    @jwt_required()
    @blp.arguments(SuperAdminUsernameSchema)
    @blp.response(201, SuperAdminUserSchema)
    def put(self, username_data, username_uuid):
        super_admin_uuid = get_jwt_identity()
        if check_super_admin(super_admin_uuid):
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


@blp.route("/users/admin/<string:username_uuid>/changePassword")
class SuperAdminPassword(MethodView):
    @jwt_required()
    @blp.arguments(SuperAdminPasswordSchema)
    @blp.response(201, SuperAdminUserSchema)
    def put(self, password_data, username_uuid):
        super_admin_uuid = get_jwt_identity()
        if check_super_admin(super_admin_uuid):
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


@blp.route("/users/superAdmins")
class SuperAdminListSuperAdmin(MethodView):
    @jwt_required()
    @blp.response(200, SuperAdminUserSchema(many=True))
    def get(self):
        super_admin_uuid = get_jwt_identity()
        super_admin = UserModel.query.filter_by(username_uuid=super_admin_uuid).first()
        if check_super_admin(super_admin_uuid) and super_admin.username == os.getenv(
            "SUPER_ADMIN_USERNAME"
        ):
            super_admins = []
            for super_admin_ in UserModel.query.all():
                print(super_admin_.role.role)
                if super_admin_.role.role == "super_admin":
                    super_admins.append(super_admin_)
            return super_admins
        else:
            abort(409, message="You can not access here!")


@blp.route("/users/superAdmin/<string:username_uuid>")
class SuperAdminSuperAdmin(MethodView):
    @jwt_required()
    @blp.response(200, SuperAdminUserSchema)
    def get(self, username_uuid):
        super_admin_uuid = get_jwt_identity()
        super_admin = UserModel.query.filter_by(username_uuid=super_admin_uuid).first()
        if check_super_admin(super_admin_uuid) and super_admin.username == os.getenv(
            "SUPER_ADMIN_USERNAME"
        ):
            super_admin_ = UserModel.query.filter_by(
                username_uuid=username_uuid
            ).first()
            return super_admin_
        else:
            abort(409, message="You can not access here!")

    @jwt_required()
    @blp.arguments(SuperAdminSuperAdminSchema)
    @blp.response(200, SuperAdminUserSchema)
    def put(self, super_admin_data, username_uuid):
        super_admin_uuid = get_jwt_identity()
        super_admin = UserModel.query.filter_by(username_uuid=super_admin_uuid).first()
        if check_super_admin(super_admin_uuid) and super_admin.username == os.getenv(
            "SUPER_ADMIN_USERNAME"
        ):
            super_admin_ = UserModel.query.filter_by(
                username_uuid=username_uuid
            ).first()
            if super_admin_data["username"] != "":
                super_admin_.username = super_admin_data["username"]
            else:
                abort(403, message="Fill this.")
            if super_admin_data["password"] != "":
                super_admin_.password = pbkdf2_sha256.hash(super_admin_data["password"])
            else:
                abort(403, message="Fill this.")
            if super_admin_data["role"] != "":
                super_admin_.role.role = super_admin_data["role"]
            else:
                abort(403, message="Fill this.")
            try:
                db.session.add(super_admin_)
                db.session.commit()
            except:
                abort(500, message="Some error has been occured while loading data!")
            return super_admin_
        else:
            abort(409, message="You can not access here!")

    @jwt_required()
    def delete(self, username_uuid):
        super_admin_uuid = get_jwt_identity()
        super_admin = UserModel.query.filter_by(username_uuid=super_admin_uuid).first()
        if check_super_admin(super_admin_uuid) and super_admin.username == os.getenv(
            "SUPER_ADMIN_USERNAME"
        ):
            super_admin_ = UserModel.query.filter_by(
                username_uuid=username_uuid
            ).first()
            if super_admin_.username == os.getenv("SUPER_ADMIN_USERNAME"):
                abort(409, message="U cant delete this")
            try:
                db.session.delete(super_admin_)
                db.session.commit()
            except:
                abort(500, message="Some error has been occured while loading data!")
        else:
            abort(409, message="You can not access here!")

        return {"message": "Super admin deleted."}


def check_super_admin(uuid):
    user = UserModel.query.filter_by(username_uuid=uuid).first()
    if user.role.role == "super_admin":
        return True
    else:
        return False
