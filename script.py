import urllib.request, json, os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    RecognizeEntitiesAction,
    AnalyzeSentimentAction,
)

class Course:
    def __init__(self, id, name, description, calendar_ics):
        self.id = id
        self.name = name
        self.description = description
        self.calendar_ics = calendar_ics

class Assignment:
    def __init__(self, id, name, description, due_at, course_id, course_inst):
        self.id = id
        self.name = name
        self.description = description
        self.due_at = due_at
        self.course_id = course_id
        self.course_inst = course_inst

courses_url = "https://canvas.instructure.com/api/v1/courses?access_token={}".format(os.environ['TOKEN'])

response = urllib.request.urlopen(courses_url)
data = response.read()
course_dict = json.loads(data)

courses = []
assignments = []

for course in course_dict:
    try:
        new_course = Course(course['id'], course['name'], course['description'], course['calendar_ics'])
        courses.append(new_course)
    except:
        print("exception occurred gathering info for course: {} - missing critical info".format(course['id']))
    try:
        url = "https://canvas.instructure.com/api/v1/courses/{}/assignments?access_token={}".format(course['id'], os.environ['TOKEN'])
        response = urllib.request.urlopen(url)
        data = response.read()
        assignments_dict = json.loads(data)

        for assignment in assignments_dict:
            try:
                new_assignment = Assignment(assignment['id'], assignment['name'], assignment['description'], assignment['due_at'], assignment['course_id'], course)
                assignments.append(new_assignment)
            except:
                print("exception occurred gathering assignment info for assignment: {} - missing critical info".format(assignment['id']))
    except:
        print("exception occurred gathering assignments for course: {}".format(course['id']))

credential = AzureKeyCredential(os.environ['TEXT_ANYL_KEY'])
text_analytics_client = TextAnalyticsClient(endpoint=os.environ['TEXT_ANYL_ENDPOINT'], credential=credential)

documents = []
for i in range(0, 9):
    documents.append({
        "id": i,
        "language": "en",
        "text": assignments[i].description
        })

poller = text_analytics_client.begin_analyze_actions(
    documents,
    display_name="Sample Text Analysis",
    actions=[
        RecognizeEntitiesAction(),
        AnalyzeSentimentAction()
    ]
)

document_results = poller.result()
for doc, action_results in zip(documents, document_results):
    recognize_entities_result, analyze_sentiment_result = action_results
    print("\nDocument text: {}".format(doc))
    print("...Results of Recognize Entities Action:")
    if recognize_entities_result.is_error:
        print("......Is an error with code '{}' and message '{}'".format(
            recognize_entities_result.code, recognize_entities_result.message
        ))
    else:
        for entity in recognize_entities_result.entities:
            print("......Entity: {}".format(entity.text))
            print(".........Category: {}".format(entity.category))
            print(".........Confidence Score: {}".format(entity.confidence_score))
            print(".........Offset: {}".format(entity.offset))

    print("...Results of Analyze Sentiment action:")
    if analyze_sentiment_result.is_error:
        print("......Is an error with code '{}' and message '{}'".format(
            analyze_sentiment_result.code, analyze_sentiment_result.message
        ))
    else:
        print("......Overall sentiment: {}".format(analyze_sentiment_result.sentiment))
        print("......Scores: positive={}; neutral={}; negative={} \n".format(
            analyze_sentiment_result.confidence_scores.positive,
            analyze_sentiment_result.confidence_scores.neutral,
            analyze_sentiment_result.confidence_scores.negative,
        ))
    print("------------------------------------------")
