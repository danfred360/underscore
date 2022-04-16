from flask import Blueprint, render_template
from flask_login import login_required, current_user
import urllib.request, json
from .models import Course, Assignment, Prioritizer
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
    db.session.add(p)
    return render_template('courses.html', p.get_courses())

@main.route('/courses/<id>')
@login_required
def detail_course(id):
    url = "https://canvas.instructure.com/api/v1/courses/{}/assignments?access_token={}".format(id, current_user.canvas_key)

    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)

    return render_template('detail_course.html', assignments=dict)