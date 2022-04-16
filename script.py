import urllib.request, json, os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    RecognizeEntitiesAction,
    AnalyzeSentimentAction,
)
from datetime import datetime
import math
from decimal import Decimal

CALL_AZURE=True

KEY_PHRASE_SCORE_WEIGHT = 1
DUE_DATE_PROXIMITY_WEIGHT = 1
POINT_IMPACT_WEIGHT = 1

class Course:
    def __init__(self, course_id, course_code, name):
        self.id = course_id
        self.course_code = course_code
        self.name = name
        self.outstanding_assignments = []
        self.completed_assignments = []

    def get_progress(self):
        # TODO url broken
        try:
            url = "https://canvas.instructure.com/api/v1/courses/{}/users/self/progress?access_token={}".format(self.id, os.environ['TOKEN'])
            response = urllib.request.urlopen(url)
            data = response.read()
            dict = json.loads(data)

            return dict
        except Exception as e:
            print("\nexception gathering course progress for course {}\n\tError - {} : {}".format(self.course_code, type(e), e))

    def get_users(self):
        try:
            url = "https://canvas.instructure.com/api/v1/courses/{}/users?access_token={}".format(self.id, os.environ['TOKEN'])
            response = urllib.request.urlopen(url)
            data = response.read()
            dict = json.loads(data)

            return dict
        except Exception as e:
            print("\nexception gathering users for course {}\n\tError - {} : {}".format(self.course_code, type(e), e))

    def get_todo_items(self):
        try:
            url = "https://canvas.instructure.com/api/v1/courses/{}/todo?access_token={}".format(self.id, os.environ['TOKEN'])
            response = urllib.request.urlopen(url)
            data = response.read()
            dict = json.loads(data)

            return dict
        except Exception as e:
            print("\nexception gathering users for course {}\n\tError - {} : {}".format(self.course_code, type(e), e))

    def __str__(self):
        return "\n{} - {}\n\tName: {}\n\tProgress: {}\n\tTODO Items: {}".format(self.id, self.course_code, self.name, self.get_progress(), self.get_todo_items())

class Assignment:
    def __init__(self, assignment_id, name, description, due_at, points_possible, course_id, course_inst, submitted):
        self.id = assignment_id
        self.name = name
        self.description = description
        self.due_at = due_at
        self.points_possible = points_possible
        self.course_id = course_id
        self.course_inst = course_inst
        self.submitted = submitted
        
        if CALL_AZURE:
            self.key_phrases = self.extract_key_phrases()
        else:
            self.key_phrases = ['not gathered, srry']
        self.key_phrase_score = self.calculate_key_phrase_score()

        due_date_proximity_arr = self.calculate_due_date_proximity_score()
        self.due_date_proximity_score = due_date_proximity_arr[1]
        self.overdue = due_date_proximity_arr[0]

        self.point_impact_score = self.calculate_point_impact_score()

        self.score = self.calculate_score()

    ######################################
    ########## Score Calulation ##########

    def calculate_score(self):
        if not self.point_impact_score == 0:
            score = (KEY_PHRASE_SCORE_WEIGHT * self.key_phrase_score) + (DUE_DATE_PROXIMITY_WEIGHT * self.due_date_proximity_score) + (POINT_IMPACT_WEIGHT * self.point_impact_score)
        else:
            score = 0
        return score

    def extract_key_phrases(self):
        credential = AzureKeyCredential(os.environ['TEXT_ANYL_KEY'])
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

    def calculate_key_phrase_score(self):
        # TODO come up with a better way to create score_phrases dictionary
        score = 100

        score_phrases = {
            "final": 100,
            "end of term": 100,
            "<strong>exam": 80,
            "Group Project": 80,
            "essay": 75,
            "Lab": 50,
            "lab": 50,
            "reference page": 50,
            "required reference page": 50,
            "online quiz": 40,
            "quiz": 50,
            "homework": 25,
            "MS Word": 10
        }

        for phrase in self.key_phrases:
            if phrase in score_phrases:
                score += score_phrases[phrase]

        return score

    def calculate_due_date_proximity_score(self):
        score = 100
        due_date_exists = True # assumed True
        overdue = False # overdue assumed False
        # calculate score exponentially by proximity to due date
        try:
            due_datetime = datetime.strptime(self.due_at, '%Y-%m-%dT%H:%M:%SZ') # "2022-02-07T04:59:59Z"
        except Exception as e:
            due_date_exists = False

        if due_date_exists:
            difference = due_datetime - datetime.now()
            if difference.total_seconds() < 0:
                overdue = True # -ln(x)

            if not overdue:
                 # score grows exponentially closer to 100 as due date gets closer
                decay = Decimal(.9)
                score = 100 * math.pow(Decimal(1) - decay, difference.days()) #.total_seconds()
                # print("Due Date Proximity Score: {} (Assignment: {})".format(score, self.name))
            else:
                if self.submitted:
                    overdue = False
                    score = 0
                else:
                    # score grows exponentially
                    decay = Decimal(.9)
                    score = 100 * math.pow(Decimal(1) + decay, difference.days())

        else:
            score = 0

        return [overdue, score]
            

        print("Assignment due date: {}".format(due_datetime))
        exit()
        return score

    def calculate_point_impact_score(self):
        score = 100

        if self.points_possible == None or self.points_possible == 0.0:
            score = 0
        # TODO calculate score using points awarded / points possible for course, taking grade weighting into account
        return score
    
    def __str__(self):
        return "\n{} - {}\nDue at: {} - Overdue: {}\nPoints Possible: {}\nCourse: {}\nKey Phrases: {}\nTotal Score: {}\nKey Phrase Score: {}\nDue Date Proximity Score: {}\nPoint Impact Score: {}".format(self.id, self.name, self.due_at, self.overdue, self.points_possible, self.course_inst.course_code, self.key_phrases, self.score, self.key_phrase_score, self.due_date_proximity_score, self.point_impact_score)

    ########## Score Calulation ##########
    ######################################


class Prioritizer:
    def __init__(self):
        self.courses = self.get_courses()

        assignments = self.get_assignments()
        self.assignments = assignments[1]
        self.outstanding_assignments = assignments[0]

    def get_courses(self):
        print("\n\t ---- getting courses ----")

        url = "https://canvas.instructure.com/api/v1/courses?per_page={}&access_token={}".format(str(50), os.environ['TOKEN'])
        response = urllib.request.urlopen(url)
        data = response.read()
        course_dict = json.loads(data)

        courses = []

        for course in course_dict:
            try:
                val = course["access_restricted_by_date"]
            except:
                # print("\n{} - {}\nDescription: {}".format(course['id'], course['course_code'], course['name']))
                new_course = Course(course['id'], course['course_code'], course['name'])
                courses.append(new_course)

        print("\n\t{} courses gathered...".format(len(courses)))

        return courses

    def get_assignments(self):

        print("\n\t ---- getting assignments ----\n")
        assignments = []
        outstanding_assignments = []

        for course in self.courses:
            try:
                url = "https://canvas.instructure.com/api/v1/courses/{}/assignments?access_token={}".format(course.id, os.environ['TOKEN'])
                response = urllib.request.urlopen(url)
                data = response.read()
                assignments_dict = json.loads(data)

                for assignment in assignments_dict:
                    try:
                        new_assignment = Assignment(assignment['id'], assignment['name'], assignment['description'], assignment['due_at'], assignment['points_possible'], assignment['course_id'], course, assignment['has_submitted_submissions'])
                        assignments.append(new_assignment)

                        if not new_assignment.submitted:
                            course.outstanding_assignments.append(new_assignment)
                            outstanding_assignments.append(new_assignment)
                        else:
                            course.completed_assignments.append(new_assignment)
                    except Exception as e:
                        if e != "list index out of range":
                            print("exception occurred gathering assignment info for assignment: {}\nError - {} : {}\n".format(assignment['name'], type(e), e.args))
                    
            except Exception as e:
                print("exception occurred gathering assignments for course: {}\nError - {} : {}".format(course.course_code, type(e), e.args))

        print("\n\t{} assignments gathered...".format(len(assignments)))

        return [outstanding_assignments, assignments]

    def prioritize_assignments(self, assignments):
        return sorted(assignments, key=lambda assignment:assignment.score, reverse=True)

    def print_assignments_all(self):
        print("\n\t---- printing un-prioritized assignment list (all) ----")
        for i in range(len(self.assignments) - 1):
            a = self.assignments[i]
            print("\nPos: {}\n{}".format(i, a))

    def print_prioritized_assignments_all(self):
        print("\n\t---- printing prioritized assignment list (all) ----")
        prioritized_assignments = self.prioritize_assignments(assignments)
        for i in range(len(prioritized_assignments) - 1):
            a = prioritized_assignments[i]
            print("\nPos: {}\n{}".format(i, a))

    def print_prioritized_assignments(self):
        print("\n\t---- printing prioritized assignment list (outstanding) ----")
        print("\nWeights - \n\tKEY_PHRASE_SCORE_WEIGHT: {}\n\tDUE_DATE_PROXIMITY_WEIGHT: {}\n\tPOINT_IMPACT_WEIGHT: {}".format(KEY_PHRASE_SCORE_WEIGHT, DUE_DATE_PROXIMITY_WEIGHT, POINT_IMPACT_WEIGHT))
        prioritized_assignments = self.prioritize_assignments(self.outstanding_assignments)
        for i in range(len(prioritized_assignments) - 1):
            a = prioritized_assignments[i]
            print("\nPos: {}\n{}".format(i, a))

p = Prioritizer()
# p.print_assignments_all()
# p.print_prioritized_assignments_all()
p.print_prioritized_assignments()
