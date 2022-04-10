import urllib.request, json, os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    RecognizeEntitiesAction,
    AnalyzeSentimentAction,
)
import datetime

class Course:
    def __init__(self, id, course_code, name):
        self.id = id
        self.course_code = course_code
        self.name = name

class Assignment:
    def __init__(self, id, name, description, due_at, points_possible, course_id, course_inst, call_azure=True):
        self.id = id
        self.name = name
        self.description = description
        self.due_at = due_at
        self.points_possible = points_possible
        self.course_id = course_id
        self.course_inst = course_inst
        if call_azure:
            self.key_phrases = self.extract_key_phrases()
        else:
            self.key_phrases = ['not gathered, srry']
        self.score = self.calculate_score()

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

    def calculate_score(self):
        score = 100

        score_phrases = {
            "final": 100,
            "end of term": 100,
            "essay": 75,
            "reference page": 50,
            "required reference page": 50,
            "quiz": 50,
            "homework": 25,
            "MS Word": 10
        }

        for phrase in self.key_phrases:
            if phrase in score_phrases:
                score += score_phrases[phrase]

        return score

class Prioritizer:
    def __init__(self):
        self.courses = self.get_courses()
        self.assignments = self.get_assignments()

    def get_courses(self):
        print("\n\t ---- getting courses ----\n")
        url = "https://canvas.instructure.com/api/v1/courses?access_token={}".format(os.environ['TOKEN'])
        response = urllib.request.urlopen(url)
        data = response.read()
        course_dict = json.loads(data)

        courses = []

        for course in course_dict:
            try:
                val = course["access_restricted_by_date"]
            except:
                # print("\n{} - {}\nDescription: {}".format(course['id'], course['course_code'], course['name']))
                new_course_obj = Course(course['id'], course['course_code'], course['name'])
                courses.append(new_course_obj)

        return courses

    def get_assignments(self):
        print("\n\t ---- getting assignments ----\n")
        assignments = []

        for course in self.courses:
            try:
                url = "https://canvas.instructure.com/api/v1/courses/{}/assignments?access_token={}".format(course.id, os.environ['TOKEN'])
                response = urllib.request.urlopen(url)
                data = response.read()
                assignments_dict = json.loads(data)

                for assignment in assignments_dict:
                    # print("\n{} - {}\nDescription: {}\nDue at: {}\nPoints Possible: {}\nCourse: {}".format(assignment['id'], assignment['name'], assignment['description'], assignment['due_at'], assignment['points_possible'], assignment['course_id']))
                    try:
                        new_assignment_obj = Assignment(assignment['id'], assignment['name'], assignment['description'], assignment['due_at'], assignment['points_possible'], assignment['course_id'], course)
                        assignments.append(new_assignment_obj)
                        # print("\n\tkeywords for assignment: {} - \n{}\n".format(new_assignment.name, new_assignment.key_phrases))
                    except Exception as e:
                        print("exception occurred gathering assignment info for assignment: {} - \n{}\n".format(assignment['id'], e))
            except Exception as e:
                print("exception occurred gathering assignments for course: {} - \n{}".format(course.id, e))
        return assignments

    def prioritize(assignments):
        pass

    def print_assignments(self):
        for i in range(len(self.assignments) - 1):
            a = self.assignments[i]
            print("\nPos: {}\n{} - {}\nDue at: {}\nPoints Possible: {}\nCourse: {}\nKey Phrases: {}\nScore: {}".format(i, a.id, a.name, a.due_at, a.points_possible, a.course_id, a.key_phrases, a.score))

    def print_prioritized_assignments(self):
        #prioritized_assignments = sorted(self.assignments, key=operator.attrgetter("score"))
        prioritized_assignments = sorted(self.assignments, key=lambda assignment:assignment.score, reverse=True)
        for i in range(len(prioritized_assignments) - 1):
            a = prioritized_assignments[i]
            print("\nPos: {}\n{} - {}\nDue at: {}\nPoints Possible: {}\nCourse: {}\nKey Phrases: {}\nScore: {}".format(i, a.id, a.name, a.due_at, a.points_possible, a.course_id, a.key_phrases, a.score))
p = Prioritizer()
p.print_prioritized_assignments()
# print(p.assignments)