from db import db

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    username_uuid = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    files = db.relationship('FilesModel', back_populates='user', lazy='dynamic', cascade='all, delete')
    role = db.relationship('UserRoleModel', uselist=False, back_populates='user')