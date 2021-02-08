import csv
import os
import sample_data
import pathlib
from datetime import datetime


DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/question.csv"
DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']


def get_formatted_headers():
    return [header.replace("_", " ").capitalize() for header in DATA_HEADER]


def get_all_questions():
    questions = []

    with open(DATA_FILE_PATH) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for row in csv_reader:
            questions.append(row)

        return questions


def sort_questions_by_time():
    questions = get_all_questions()
    new_list = sorted(questions, key=lambda k: k['submission_time'])

    for question in new_list:
        time_stamp = int(question["submission_time"])
        dt_object = datetime.fromtimestamp(time_stamp)
        question["submission_time"] = dt_object

    return new_list


def get_question_by_id(id):
    questions = sort_questions_by_time()

    for question in questions:
        if question["id"] == id:
            return question


