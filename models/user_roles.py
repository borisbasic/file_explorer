from db import db

class UserRoleModel(db.Model):
    __tablename__ = 'userroles'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String)
    username_uuid = db.Column(db.String, db.ForeignKey('users.username_uuid'))
    user = db.relationship('UserModel', back_populates='role')