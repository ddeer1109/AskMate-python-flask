from datetime import datetime
from data_handler import get_all_questions, get_all_answers


def get_formatted_headers(headers):
        return [header.replace("_", " ").capitalize() for header in headers]


def sort_data_by_time(entries_list):
    new_list = sorted(entries_list, key=lambda k: k['submission_time'])

    return [convert_timestamp(entry) for entry in new_list]


def convert_timestamp(entry):

    time_stamp = int(entry["submission_time"])
    dt_object = datetime.fromtimestamp(time_stamp)
    entry["submission_time"] = dt_object

    return entry


def get_question_by_id(question_id):

    questions = get_all_questions()

    for question in questions:
        if question["id"] == question_id:
            return convert_timestamp(question)


def get_answers_for_question(question_id):
    answers = get_all_answers()

    question_answers = []

    for answer in answers:
        if answer["id"] == question_id:
            question_answers.append(convert_timestamp(answer))

    return question_answers


def filter_data(dict_data, headers):
    filtered_data = []

    for entry in dict_data:
        filtered_entry = {}
        for header in headers:
            filtered_entry[header] = entry[header]
        filtered_data.append(filtered_entry)

    return filtered_data


