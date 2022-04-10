from flask import Blueprint, render_template
from flask_login import login_required, current_user
import urllib.request, json
from . import db

dash = Blueprint('dashboard', __name__)

@dash.route('/dash')
@login_required
def dashboard():
    courses_url = "https://canvas.instructure.com/api/v1/courses?access_token={}".format(current_user.canvas_key)

    response = urllib.request.urlopen(url)
    data = response.read()
    course_dict = json.loads(data)

    assignments = []

    for course in course_dict:
        assignments_url = "https://canvas.instructure.com/api/v1/courses/{}/assignments?access_token={}".format(course['id'], current_user.canvas_key)
        data = response.read()
        assignments_dict = json.loads(data)
        assignments.append(assignments_dict)
    return render_template('dashboard.html', assignments=assignments)