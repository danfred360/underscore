# underscore
MS Teams app that integrates with Canvas to assist groups in prioritizing upcoming assignments. Uses Azure Text Analysis API to analyze assignments.

## runnning web app locally

flask environment variables
```bash
export FLASK_APP=project
export FLASK_DEBUG=1
export TOKEN=<your-canvas-integration-token>
export TEXT_ANYL_KEY=<your-azure-text-anyl-key>
export TEXT_ANYL_ENDPOINT=<azure-text-anyl-resource-endpoint-url>
```

install required packages
```bash
pip install -r requirments.txt # use a virtual env
```

create database for flask app (run in python REPL)
```python
from project import db, create_app, models
db.create_all(app=create_app()) # pass the create_app result so Flask-SQLAlchemy gets the configuration.
```

api call to get courses
```bash
curl -H "Authorization: Bearer $token" "https://canvas.instructure.com/api/v1/courses" | jq 
. > courses.json
```

api call to get assignments
```bash
curl -H "Authorization: Bearer $token" "https://canvas.instructure.com/api/v1/courses/$COURSE_ID/assignments" | jq . > assignments.json  
```
