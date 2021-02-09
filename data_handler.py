import csv
import os
import sample_data
import pathlib
from datetime import datetime


QUESTIONS_DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/question.csv"
ANSWER_DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/answer.csv"
QUESTIONS_DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_DATA_HEADER = ['id','submission_time','vote_number','message','image']


def get_formatted_headers(datatype="question"):
    if datatype == "question":
        return [header.replace("_", " ").capitalize() for header in QUESTIONS_DATA_HEADER]
    elif datatype == "answer":
        return [header.replace("_", " ").capitalize() for header in ANSWERS_DATA_HEADER]


def get_all_questions():
    questions = []

    with open(QUESTIONS_DATA_FILE_PATH) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for row in csv_reader:
            questions.append(row)

        return questions


def get_all_answers():
    answers = []

    with open(ANSWER_DATA_FILE_PATH) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for row in csv_reader:
            answers.append(row)

        return answers


def sort_data_by_time(entries_list):
    new_list = sorted(entries_list, key=lambda k: k['submission_time'])

    for entry in new_list:
        time_stamp = int(entry["submission_time"])
        dt_object = datetime.fromtimestamp(time_stamp)
        entry["submission_time"] = dt_object

    return new_list


def get_question_by_id(id):
    questions_unformatted = get_all_questions()
    questions = sort_data_by_time(questions_unformatted)

    for question in questions:
        if question["id"] == id:
            return question


def get_answers_for_question(question_id):
    answers = sort_data_by_time(get_all_answers())

    question_answers = []

    for answer in answers:
        if answer["id"] == question_id:
            question_answers.append(answer)

    return question_answers




