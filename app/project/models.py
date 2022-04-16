from flask_login import UserMixin
from . import db

association_table = db.Table('association', db.metadata,
    db.Column('user_id', db.ForeignKey('user.id')),
    db.Column('assignment_id', db.ForeignKey('assignment.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    canvas_key = db.Column(db.String(100))
    outstanding_assignments = db.relationship(
        "Assignment",
        secondary=association_table,
        back_populates="Users"
    )

class Course(dd.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(1000), unique=True)
    name = db.Column(db.String(1000))

