from marshmallow import Schema, fields
from flask_smorest.fields import Upload


class AddFileSchema(Schema):
    name = fields.Str(required=True, dump_only=True)
    username = fields.Str()
    file = Upload()
    time_created = fields.Str(dump_only=True)
    ext = fields.Str(dump_only=True)
    name_uuid = fields.Str(dump_only=True)
    username_uuid = fields.Str(dump_only=True)


class RoleSchema(Schema):
    role = fields.Str(dump_only=True)
    username_uuid = fields.Str(dump_only=True)


class RegisterSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    password = fields.Str(load_only=True)
    username_uuid = fields.Str(dump_only=True)
    files = fields.List(fields.Nested(AddFileSchema), dump_only=True)
    role = fields.Nested(RoleSchema, dump_only=True)
    role_ = fields.Str(load_only=True)


class LoginSchema(Schema):
    username = fields.Str()
    password = fields.Str(load_only=True)


class SuperAdminUserSchema(Schema):
    username = fields.Str()
    role = fields.Nested(RoleSchema, dump_only=True)
    password = fields.Str()


class SuperAdminRoleSchema(Schema):
    role = fields.Str()


class SuperAdminUsernameSchema(Schema):
    username = fields.Str()


class SuperAdminPasswordSchema(Schema):
    password = fields.Str()


class SuperAdminSuperAdminSchema(Schema):
    username = fields.Str()
    password = fields.Str()
    role = fields.Str()
