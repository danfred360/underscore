from flask_login import UserMixin
from . import db

# https://docs.sqlalchemy.org/en/14/core/type_basics.html

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    canvas_key = db.Column(db.String(100))

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(1000), unique=True)
    name = db.Column(db.String(1000))

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    name = db.Column(db.String(1000))
    description = db.Column(db.UnicodeText)
    due_at = db.Column(db.Integer) # time?
    points_possible = db.Column(db.Integer)
    submitted = db.Column(db.Boolean)
    overdue = db.Column(db.Boolean)
    score = db.Column(db.Integer)
    key_phrase_score = db.Column(db.Integer)
    due_date_proximity_score = db.Column(db.Integer)
    point_impact_score = db.Column(db.Integer)

