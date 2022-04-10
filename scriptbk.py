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
    def __init__(self, id, name, description, due_at, allowed_extensions, points_possible, course_id, course_inst):
        self.id = id
        self.name = name
        self.description = description
        self.due_at = due_at
        self.allowed_extensions = allowed_extensions
        self.points_possible = points_possible
        self.course_id = course_id
        self.course_inst = course_inst
        self.key_phrases = self.extract_key_phrases()

    def extract_key_phrases(self):
        credential = AzureKeyCredential('447b1fc8efcf4e998cae155f64976c5c')
        endpoint = os.environ['TEXT_ANYL_ENDPOINT']

        text_analytics_client = TextAnalyticsClient(endpoint, credential)

        documents = [{
            "id": self.id,
            "language": "en",
            "text": self.description
        }]

        response = text_analytics_client.extract_key_phrases(documents, language="en")
        result = [doc for doc in response if not doc.is_error]

        return result[0].key_phrases

class Prioritizer:
    def __init__(self):
        c_resp = self.rip_canvas()
        self.courses = c_resp[0]
        self.assignments = c_resp[1]

    def recognize_linked_entities(self, assignment):
        credential = AzureKeyCredential('447b1fc8efcf4e998cae155f64976c5c')
        endpoint = os.environ['TEXT_ANYL_ENDPOINT']

        text_analytics_client = TextAnalyticsClient(endpoint, credential)

        documents = [{
            "id": i,
            "language": "en",
            "text": assignments.description
        }]

        response = text_analytics_client.recognize_linked_entities(documents, language="en")
        result = [doc for doc in response if not doc.is_error]

        for doc in result:
            for entity in doc.entities:
                print("Entity: {}".format(entity.name))
                print("...URL: {}".format(entity.url))
                print("...Data Source: {}".format(entity.data_source))
                print("...Entity matches:")
                for match in entity.matches:
                    print("......Entity match text: {}".format(match.text))
                    print("......Confidence Score: {}".format(match.confidence_score))
                    print("......Offset: {}".format(match.offset))

    def rip_canvas(self):
        courses_url = "https://canvas.instructure.com/api/v1/courses?access_token={}".format(os.environ['TOKEN2'])

        response = urllib.request.urlopen(courses_url)
        data = response.read()
        course_dict = json.loads(data)

        courses = []
        assignments = []
        current_course = ''

        for course in course_dict:
            try:
                new_course = Course(course['id'], course['name'], course['description'], course['calendar_ics'])
                courses.append(new_course)
                current_course = new_course
            except:
                print("exception occurred gathering info for course: {} - missing critical info".format(course['id']))
            try:
                url = "https://canvas.instructure.com/api/v1/courses/{}/assignments?access_token={}".format(course['id'], os.environ['TOKEN2'])
                response = urllib.request.urlopen(url)
                data = response.read()
                assignments_dict = json.loads(data)

                for assignment in assignments_dict:
                    if len(assignments) < 10:
                        try:
                            new_assignment = Assignment(assignment['id'], assignment['name'], assignment['description'], assignment['due_at'], assignments['allowed_extensions'], assignment['points_possible'], assignment['course_id'], current_course)
                            assignments.append(new_assignment)
                            # print("\n\tkeywords for assignment: {} - \n{}\n".format(new_assignment.name, new_assignment.key_phrases))
                        except Exception as e:
                            print("exception occurred gathering assignment info for assignment: {} - \n{}\n".format(assignment['id'], e))
                    else:
                        print("10 assignments reached -- skipping azure api call")
            except Exception as e:
                print("exception occurred gathering assignments for course: {} - \n{}".format(course['id'], e))

        return[course, assignments]

    def print_prioritized_assignments(self):
        for i in range(len(self.assignments)):
            a = self.assignments[i]
            print("{} : {}\nCourse: {}\nDescription: {}\nDue Date:{}\n".format(i, a.name, a.course_inst.name, a.description, a.due_at))

p = Prioritizer()
# p.print_prioritized_assignments()
print(p.assignments)