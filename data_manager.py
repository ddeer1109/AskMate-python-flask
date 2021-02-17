from datetime import datetime
import data_handler
import time
import operator
import os


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


def get_entry_by_id(entry_id, entries_list):
    for entry in entries_list:
        if entry['id'] == entry_id:
            return entry


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


def get_next_id(entries_list):
    next_id = 0
    for entry in entries_list:
        entry_id = int(entry['id'])
        if entry_id >= next_id:
            next_id = entry_id

    return next_id + 1


def delete_rows(question_id, criteria, entries_list):
    temp_list = []

    for entry in entries_list:
        if entry[criteria] != question_id:
            temp_list.append(entry)
        else:
            if entry['image'] != 'none.jpg':
                if criteria == 'id':
                    sub_dir = 'questions'
                else:
                    sub_dir = 'answers'
                data_handler.delete_image(entry['image'], sub_dir, entry['id'])

    return temp_list


def get_current_timestamp():
    return int(time.time())


def set_initial_values(entry_dictionary, listed_base_data):
    entry_dictionary['submission_time'] = str(get_current_timestamp())
    entry_dictionary['vote_number'] = '0'
    entry_dictionary['id'] = str(get_next_id(listed_base_data))


def add_new_question(form_data, request_files):
    questions = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)
    requested_data = dict(form_data)

    set_initial_values(requested_data, questions)
    requested_data['view_number'] = '0'

    image_filename = process_image_input(
        request_files['image'],
        'questions',
        requested_data['id'])

    requested_data['image'] = image_filename

    questions.append(requested_data)
    data_handler.write_file(data_handler.QUESTIONS_DATA_FILE_PATH, data_handler.QUESTIONS_DATA_HEADER, questions)
    return requested_data['id']


def add_new_answer(form_data, request_files, question_id):
    answers = data_handler.read_file(data_handler.ANSWER_DATA_FILE_PATH)
    requested_data = dict(form_data)

    set_initial_values(requested_data, answers)
    requested_data['question_id'] = str(question_id)

    image_filename = process_image_input(
        request_files['image'],
        'answers',
        requested_data['id'])

    requested_data['image'] = image_filename

    answers.append(requested_data)
    data_handler.write_file(data_handler.ANSWER_DATA_FILE_PATH, data_handler.ANSWERS_DATA_HEADER, answers)


def process_image_input(image_storage_obj, sub_dir, entry_id):
    """Checks if storage object is not empty. If it is returns default image filename else returns object filename"""
    storage_obj_empty = image_storage_obj.filename == ""
    invalid_extension = ".jpg" not in image_storage_obj.filename and ".png" not in image_storage_obj.filename

    if storage_obj_empty or invalid_extension:
        image_name = 'none.jpg'
    else:
        data_handler.save_image(image_storage_obj, sub_dir, entry_id)
        image_name = image_storage_obj.filename

    return image_name


def update_entry(updated_entry, entries_list):
    for entry in entries_list:
        if entry['id'] == updated_entry['id']:
            entries_list[entries_list.index(entry)] = updated_entry


def vote_on_post(entry_id, vote_value, entry_type):
    if entry_type == "question":
        entries_list = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)
    else:
        entries_list = data_handler.read_file(data_handler.ANSWER_DATA_FILE_PATH)

    entry = get_entry_by_id(entry_id, entries_list)

    if vote_value == "vote_up":
        entry["vote_number"] = str(int(entry["vote_number"]) + 1)
    else:
        entry["vote_number"] = str(int(entry["vote_number"]) - 1)

    update_entry(entry, entries_list)

    if entry_type == "answer":
        data_handler.write_file(data_handler.ANSWER_DATA_FILE_PATH, data_handler.ANSWERS_DATA_HEADER, entries_list)
        id_of_questions_to_redirect = entry['question_id']
    else:
        data_handler.write_file(data_handler.QUESTIONS_DATA_FILE_PATH, data_handler.QUESTIONS_DATA_HEADER, entries_list)
        id_of_questions_to_redirect = entry_id

    return id_of_questions_to_redirect


def edit_entry(form_data, entry, entries_list):
    entry['message'] = form_data['message']
    entry['vote_number'] = '0'

    if 'question_id' not in entry.keys():
        entry['title'] = form_data['title']
        database_path = data_handler.QUESTIONS_DATA_FILE_PATH
        database_headers = data_handler.QUESTIONS_DATA_HEADER
    else:
        database_path = data_handler.ANSWER_DATA_FILE_PATH
        database_headers = data_handler.ANSWERS_DATA_HEADER

    update_entry(entry, entries_list)
    data_handler.write_file(database_path, database_headers, entries_list)





