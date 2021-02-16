from datetime import datetime
import data_handler
import time
import operator


def get_formatted_headers(headers):
    return [header.replace("_", " ").capitalize() for header in headers]

def sort_data(questions, requested_query_string, header):
    sorting_key = {
        'order_by': 'submission_time',
        'order_direction': 'desc'
    }

    if len(requested_query_string) == 0:
        requested_query_string = sorting_key

    questions = filter_data(sort_data_by_sorting_key(questions, requested_query_string), header)

    return questions

def sort_data_by_sorting_key(entries_list, sorting_key):
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
    converted_time = datetime.fromtimestamp(time_stamp)
    entry["submission_time"] = converted_time

    return entry

def get_question_by_id(question_id, questions):
    for question in questions:
        if question["id"] == question_id:
            return convert_timestamp(question)

def get_question_by_id_without_timestamp_conversion(question_id, questions):
    for question in questions:
        if question["id"] == question_id:
            return question


def get_answers_for_question(question_id, answers):
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


def get_next_id(questions):
    next_id = 0
    for question in questions:
        question_id = int(question['id'])
        if question_id >= next_id:
            next_id = question_id

    return next_id + 1

def get_next_answer_id(answers):
    next_id = 0
    for answer in answers:
        answer_id = int(answer['id'])
        if answer_id >= next_id:
            next_id = answer_id
    return next_id + 1


def delete_rows(question_id, criteria, entries_list):
    temp_list = []

    for entry in entries_list:
        if entry[criteria] != question_id:
            temp_list.append(entry)

    return temp_list

def get_current_timestamp():
    return int(time.time())
