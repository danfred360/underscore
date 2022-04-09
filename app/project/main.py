from flask import Blueprint, render_template
from flask_login import login_required, current_user
import urllib.request, json
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/assignments')
@login_required
def assignments():
    assignments = []

    url = "https://canvas.instructure.com/api/v1/courses?access_token={}".format(current_user.canvas_key)

    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)

    return render_template('assignments.html', assignments=dict["results"])