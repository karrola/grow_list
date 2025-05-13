from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_title = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tasks = db.relationship('Task', backref='list', cascade='all, delete-orphan', lazy=True)
    is_default = db.Column(db.Boolean, default=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(100))
    lists = db.relationship('List', backref='user', cascade='all, delete-orphan', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)
    if_done = db.Column(db.Boolean, default = False)
    deadline_date = db.Column(db.Date, nullable=True, default = None)
    deadline_time = db.Column(db.Time, nullable=True, default = None)