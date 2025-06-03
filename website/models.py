from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

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
    water_points = db.Column(db.Integer, default=0)
    plant_growth = db.Column(db.Integer, default=0)
    plants = db.relationship('Plant', backref='owner', lazy=True)
    daily_task_goal = db.Column(db.Integer, default=1)
    daily_checked_tasks = db.Column(db.Integer, default=0)
    plant_wither_stage = db.Column(db.Integer, default=0)
    plant_rescue_progress = db.Column(db.Integer, default=0)
    plant_unwatered_days = db.Column(db.Integer, default=0)
    plant_withered_notification_sent = db.Column(db.Boolean, default=False)
    plant_created_at = db.Column(db.DateTime)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='tasks')
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)
    if_done = db.Column(db.Boolean, default = False)
    deadline_date = db.Column(db.Date, nullable=True, default = None)
    deadline_time = db.Column(db.Time, nullable=True, default = None)
    reminder = db.Column(db.Boolean, default=False)
    reminder_sent = db.Column(db.Boolean, default=False)
    first_check = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    finished_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    final_growth = db.Column(db.Integer)
    final_wither_stage = db.Column(db.Integer)