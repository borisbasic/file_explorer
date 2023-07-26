from db import db

class FilesModel(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    name_uuid = db.Column(db.String, nullable=False)
    time_created = db.Column(db.DateTime, nullable=False)
    username = db.Column(db.String, nullable=False)
    username_uuid = db.Column(db.String, db.ForeignKey('users.username_uuid'))
    user = db.relationship('UserModel', back_populates='files')
    ext = db.Column(db.String, nullable=False)    