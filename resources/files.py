import os
import json
import datetime
import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity, get_current_user, get_jti, get_csrf_token,\
get_jwt_header, get_jwt_request_location, current_user
from sqlalchemy import and_
from db import db

blp = Blueprint('/file_explorer', __name__, description='Upload docs, pics')

from schemas import AddFileSchema
from models import FilesModel, UserModel



'''@blp.route('/show_all_files')
class ShowFile(MethodView):
    @jwt_required()
    @blp.response(200, AddFileSchema(many=True))
    def get(self):
        username_uuid = get_jwt_identity()
        user = UserModel.query.filter_by(username_uuid=username_uuid).first()
        if user.role == 'admin':
            files = FilesModel.query.all()
        else:
            abort()
        return files
'''
@blp.route('/show_files')
class ShowFileByUser(MethodView):
    @jwt_required()
    @blp.response(200, AddFileSchema(many=True))
    def get(self):
        username_uuid = get_jwt_identity()
        user = UserModel.query.filter_by(username_uuid=username_uuid).first()
        if user.role.role == 'user':
            files = user.files
        elif user.role.role == 'admin':
            files = FilesModel.query.all()
        elif user.role.role == 'super_admin':
            files = FilesModel.query.all()
        else:
            abort(500, message='Access is not ava...')
        return files

@blp.route('/add_files')
class AddFileByUser(MethodView):
    @jwt_required()
    @blp.arguments(AddFileSchema, location='files')
    @blp.response(200, AddFileSchema)
    def post(self, file_data):
        username_uuid = get_jwt_identity()
        user = UserModel.query.filter_by(username_uuid=username_uuid).first()
        docs_dir = os.getenv('UPLOAD_FOLDER')
        file = file_data['file']
        ext = file.filename.split('.')[-1]
        if ext not in os.getenv('ALLOWED_EXT') or ext == '':
            abort(400, 
            message="File is not right extension. Allowed extensions are 'jpg','png','jpeg', 'txt', 'doc', 'docx', 'pdf', 'gif'")
        if user.username_uuid not in os.listdir('static'):
            os.mkdir(os.path.join('static', user.username_uuid))
        name_uuid = uuid.uuid4().hex
        file.save(os.path.join(docs_dir+'/'+user.username_uuid, secure_filename(str(name_uuid+file.filename))))
        new_file = FilesModel(name=name_uuid+file.filename, name_uuid = name_uuid,
        time_created=datetime.datetime.now(), username=user.username, username_uuid=username_uuid, ext=ext)
        try:
            db.session.add(new_file)
            db.session.commit()
        except:
            abort(500, message='An error occured while loading data')
        return new_file


@blp.route('/show_files/<string:file_name_uuid>')
class UserFile(MethodView):
    @jwt_required()
    @blp.response(200, AddFileSchema)
    def get(self, file_name_uuid):
        username_uuid = get_jwt_identity()
        file = FilesModel.query.filter(and_(FilesModel.username_uuid==username_uuid,
                                             FilesModel.name_uuid==file_name_uuid)).first()
        if not file:
            abort(404, message='No such file')
        return file

    @jwt_required()
    def delete(self, file_name_uuid):
        username_uuid = get_jwt_identity()
        file = FilesModel.query.filter(and_(FilesModel.username_uuid==username_uuid,
                                             FilesModel.name_uuid==file_name_uuid)).first()
        if not file:
            abort(404, message='No such file')
        docs_dir = os.getenv('UPLOAD_FOLDER')
        os.remove(docs_dir+'/'+username_uuid+'/'+file.name)
        db.session.delete(file)
        db.session.commit()
        return {'message':'File successfully deleted!'}

    @jwt_required()
    @blp.arguments(AddFileSchema, location='files')
    @blp.response(200, AddFileSchema)
    def put(self, file_data, file_name_uuid):
        username_uuid = get_jwt_identity()
        file_ = FilesModel.query.filter(and_(FilesModel.username_uuid==username_uuid, 
                                             FilesModel.name_uuid==file_name_uuid)).first()
        if not file_:
            abort(404, message='No such file.')
        new_file = file_data['file']
        docs_dir = os.getenv('UPLOAD_FOLDER')
        ext = new_file.filename.split('.')[-1]
        if ext not in os.getenv('ALLOWED_EXT') or ext == '':
            abort(400, 
            message="File is not right extension. Allowed extensions are 'jpg','png','jpeg', 'txt', 'doc', 'docx', 'pdf', 'gif'")
        os.remove(docs_dir+'/'+username_uuid+'/'+file_.name)
        name_uuid = uuid.uuid4().hex
        file_.name_uuid = name_uuid
        file_.name = name_uuid+new_file.filename
        file_.time_created = datetime.datetime.now()
        new_file.save(os.path.join(docs_dir+'/'+username_uuid, secure_filename(str(name_uuid+new_file.filename))))
        
        try:
            db.session.add(file_)
            db.session.commit()
        except:
            abort(500, message='An error occured while loading data')
        return file_
    