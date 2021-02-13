from datetime import datetime
from data_handler import get_all_questions, get_all_answers, save_all_answers, save_all_questions
import time
import operator


def get_formatted_headers(headers):
    return [header.replace("_", " ").capitalize() for header in headers]


def sort_data_by_time(entries_list):
    new_list = sorted(entries_list, key=lambda k: k['submission_time'])

    return [convert_timestamp(entry) for entry in new_list]


def sort_data_by_sorting_key(entries_list, sorting_key):
    sorting_key = dict(sorting_key)
    print(sorting_key)

    if sorting_key['order_by'] in ['view_number', 'vote_number']:
        # it is necessary to cast value to int to use function sort
        for entry in entries_list:
            entry[sorting_key['order_by']] = int(entry[sorting_key['order_by']])

        new_list = sorted(entries_list, key=lambda k: k[sorting_key['order_by']],
                          reverse=True if sorting_key['order_direction'] == 'desc' else False)
    else:
        new_list = sorted(entries_list, key=lambda k: k[sorting_key['order_by']].lower(),
                          reverse=True if sorting_key['order_direction'] == 'desc' else False)
    return [convert_timestamp(entry) for entry in new_list]


def convert_timestamp(entry):
    time_stamp = int(entry["submission_time"])
    dt_object = datetime.fromtimestamp(time_stamp)
    entry["submission_time"] = dt_object

    return entry

# TODO - add questions_list as parameter
def get_question_by_id(question_id):
    questions = get_all_questions()

    for question in questions:
        if question["id"] == question_id:
            return convert_timestamp(question)

# TODO - add questions_list as parameter
def get_answers_for_question(question_id):
    answers = get_all_answers()

    question_answers = []

    for answer in answers:
        if answer["question_id"] == question_id:
            question_answers.append(convert_timestamp(answer))

    return question_answers


def filter_data(dict_data, headers):
    filtered_data = []
    try:
        for entry in dict_data:
            filtered_entry = {}
            for header in headers:
                filtered_entry[header] = entry[header]
            filtered_data.append(filtered_entry)

        return filtered_data
    # eliminate error occurring when empty dict_data filtered
    except TypeError:
        return []


# TODO - add questions_list as parameter
def get_next_id():
    questions = get_all_questions()
    next_id = 0
    for question in questions:
        question_id = int(question['id'])
        if question_id >= next_id:
            next_id = question_id

    return next_id + 1

# TODO - add answers_list as parameter
def get_next_answer_id():
    answers = get_all_answers()
    next_id = 0
    for answer in answers:
        answer_id = int(answer['id'])
        if answer_id >= next_id:
            next_id = answer_id
    return next_id + 1

# TODO - add questions_list as parameter
def delete_question(question_id):
    questions = list(get_all_questions())
    for question in questions:
        print(question)
        if question[0] == question_id:
            questions.remove(question)
    return questions

# def convert_ordered_dict_to_regular_dictionary_list(question_id):
#     answers = get_all_answers()
#     temp_answers = []
#     for answer in answers:
#         temp_answers.append(dict(answer))
#     return temp_answers

# TODO - add answers_list as parameter and return answers_list
def delete_answers_by_question_id(question_id):
    answers = get_all_answers()
    temp = []
    for answer in answers:
        if answer['question_id'] != question_id:
            temp.append(answer)
    save_all_answers(temp)

# TODO - add questions_list as parameter and return questions_list
def delete_question_by_id(question_id):
    questions = get_all_questions()
    temp = []
    for question in questions:
        if question['id'] != question_id:
            temp.append(question)
    save_all_questions(temp)

def get_current_timestamp():
    return int(time.time())
