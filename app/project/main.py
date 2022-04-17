from flask import Blueprint, render_template
from flask_login import login_required, current_user
import urllib.request, json
from .models import Course, Assignment
from .workers import Prioritizer
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

# @main.route('/courses')
# @login_required
# def courses():
#     url = "https://canvas.instructure.com/api/v1/courses?access_token={}".format(current_user.canvas_key)

#     response = urllib.request.urlopen(url)
#     data = response.read()
#     dict = json.loads(data)

#     return render_template('courses.html', courses=dict)

@main.route('/courses')
@login_required
def courses():
    p = Prioritizer(current_user)
    courses = []
    for course in p.get_courses():
        new_course = Course(id=course.id, course_code=course.course_code, name=course.name)
        courses.append(new_course)
        db.session.add(new_course)
    return render_template('courses.html', courses=courses)

@main.route('/courses/<id>')
@login_required
def detail_courses(id):
    return render_template('detail_course.html', assignments=get_assignments(id))


def get_assignments(course_id):
    assignments = []

    p = Prioritizer(current_user)
    assignment_objects = p.get_assignments(course_id)
    for assignment in assignment_objects[1]:
        new_assignment = Assignment(
            id = assignment.id,
            course_id = assignment.course_id,
            name = assignment.name,
            description = assignment.description,
            due_at = assignment.due_at,
            points_possible = assignment.points_possible,
            submitted = assignment.submitted,
            overdue = assignment.overdue,
            score = assignment.score,
            key_phrase_score = assignment.key_phrase_score,
            due_date_proximity_score = assignment.due_date_proximity_score,
            point_impact_score = assignment.point_impact_score
        )
        assignments.append(new_assignment)
        db.session.add(new_assignment)
    return assignments



# @main.route('/courses/<id>')
# @login_required
# def detail_course(id):
#     url = "https://canvas.instructure.com/api/v1/courses/{}/assignments?access_token={}".format(id, current_user.canvas_key)

#     response = urllib.request.urlopen(url)
#     data = response.read()
#     dict = json.loads(data)

#     return render_template('detail_course.html', assignments=dict)