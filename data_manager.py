from psycopg2.extras import RealDictCursor
from datetime import datetime

import data_handler
import time


@data_handler.connection_handler
def get_all_data(cursor: RealDictCursor) -> list:

    query = """
        SELECT *
        FROM question
        ORDER BY submission_time"""

    cursor.execute(query)
    data = cursor.fetchall()
    return data


@data_handler.connection_handler
def get_question_by_id(cursor: RealDictCursor, id_string: str):
    # question_id = int(id_string)

    query = """
            SELECT *
            FROM question
            WHERE id=%(question_id)s
    """

    cursor.execute(query, {'question_id': id_string})
    return cursor.fetchone()


@data_handler.connection_handler
def get_answers_for_question(cursor: RealDictCursor, question_id_int: int):

    query = """
                SELECT *
                FROM answer
                WHERE question_id=%(question_id)s
        """

    cursor.execute(query, {'question_id': question_id_int})
    return cursor.fetchall()


@data_handler.connection_handler
def add_new_entry(cursor: RealDictCursor, table_name: str, form_data=None, request_files=None, question_id=None):

    complete_dict_data = init_complete_dict_entry(
                                                    table_name,
                                                    form_data,
                                                    request_files,
                                                    question_id)

    columns_sql_str = ", ".join([str(key) for key in complete_dict_data.keys()])
    values_sql_str = ", ".join(f'%({key})s' for key in complete_dict_data.keys())

    comment = f"""
        INSERT INTO 
        {table_name} ({columns_sql_str})
        VALUES ({values_sql_str})
        RETURNING id
    """

    cursor.execute(comment, complete_dict_data)
    entry_id = str(cursor.fetchone()['id'])

    if request_files['image'].filename:

        if table_name == 'question':
            data_handler.save_image(request_files['image'], 'questions', entry_id)
        elif table_name == 'answer':
            data_handler.save_image(request_files['image'], 'answers', entry_id)

    if table_name == 'question':
        return entry_id


def set_init_entry_values(form_data, request_files):
    requested_data = dict(form_data)
    image_filename = get_image_name(request_files['image'])

    requested_data['image'] = image_filename
    requested_data['vote_number'] = 0
    requested_data['submission_time'] = datetime.fromtimestamp(time.time())

    return requested_data


def init_complete_dict_entry(entry_type, form_data=None, request_files=None, question_id=None):

    if entry_type == 'question':
        complete_entry = set_init_entry_values(form_data, request_files)
        complete_entry['view_number'] = 0

    elif entry_type == 'answer':
        complete_entry = set_init_entry_values(form_data, request_files)
        complete_entry['question_id'] = question_id

    elif entry_type == 'comment':
        pass

    elif entry_type == 'question_tag':
        pass

    elif entry_type == 'tag':
        pass

    return complete_entry


@data_handler.connection_handler
def delete_answer_by_id(cursor: RealDictCursor, answer_id: str):
    comment = """
    DELETE 
    FROM answer
    WHERE id=%(id)s
    RETURNING question_id
    """

    cursor.execute(comment, {'id': answer_id})

    question_id = cursor.fetchone()['question_id']
    return question_id


@data_handler.connection_handler
def delete_answers_by_question_id(cursor: RealDictCursor, question_id):
    comment = """
        DELETE 
        FROM answer
        WHERE question_id=%(question_id)s
        RETURNING id, image
        """

    cursor.execute(comment, {'question_id': question_id})

    deleted_data = cursor.fetchall()

    for single_data in deleted_data:
        data_handler.delete_image(single_data['image'], 'answers', single_data['id'])


@data_handler.connection_handler
def delete_question(cursor: RealDictCursor, question_id: str):

    delete_answers_by_question_id(question_id)

    comment = """
    DELETE 
    FROM question
    WHERE id=%(question_id)s
    RETURNING id, image
    """

    cursor.execute(comment, {'question_id': question_id})

    deleted_data = cursor.fetchone()
    data_handler.delete_image(deleted_data['image'], 'questions', deleted_data['id'])

@data_handler.connection_handler
def get_answer(cursor: RealDictCursor, answer_id):
    query = """
        SELECT * FROM answer
        WHERE id = %(answer_id)s
    """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()

@data_handler.connection_handler
def save_edited_answer(cursor: RealDictCursor, answer_id, message):
    comment = """
        UPDATE answer
        SET message = %(message)s
        WHERE id=%(answer_id)s
        RETURNING question_id
    """

    cursor.execute(comment, {'answer_id': answer_id, 'message': message})
    question_id = cursor.fetchone()['question_id']
    return question_id

@data_handler.connection_handler
def save_edited_question(cursor: RealDictCursor, question_id, title, message):
    comment = """
        UPDATE question
        SET title = %(title)s, message = %(message)s
        WHERE id = %(question_id)s
    """

    cursor.execute(comment, {'question_id': question_id, 'title': title, 'message': message})

@data_handler.connection_handler
def get_single_question(cursor: RealDictCursor, question_id):
    query = """
        SELECT *
        FROM question
        WHERE id = %(question_id)s
    """

    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchone()


@data_handler.connection_handler
def vote_on_post(cursor: RealDictCursor, entry_id, vote_value, entry_type):
    params = {'entry_id': entry_id}
    if entry_type == 'answer':
        selection_query = 'id, vote_number, question_id'
    elif entry_type == 'question':
        selection_query = 'id, vote_number'

    query = f"""
    SELECT {selection_query}
    FROM {entry_type}
    WHERE id=%(entry_id)s"""

    cursor.execute(query, params)
    fetched_data = cursor.fetchone()

    if vote_value == 'vote_up':
        new_vote_value = fetched_data['vote_number'] + 1
    else:
        new_vote_value = fetched_data['vote_number'] - 1
    params['new_vote_value'] = new_vote_value

    comment = f"""
    UPDATE {entry_type}
    SET vote_number = %(new_vote_value)s
    WHERE id=%(entry_id)s"""
    cursor.execute(comment, params)

    if entry_type == 'answer':
        return fetched_data['question_id']
    elif entry_type == 'question':
        return fetched_data['id']




#
# def sort_data(questions, requested_query_string, header):
#     """Returns data (for this feature implemented for questions) sorted by requested_query_string"""
#
#     sorting_key = {
#         'order_by': 'submission_time',
#         'order_direction': 'desc'
#     }
#
#     if len(requested_query_string) == 0:
#         requested_query_string = sorting_key
#
#     questions = filter_data(sort_data_by_sorting_key(questions, requested_query_string), header)
#
#     return questions
#
#
# def sort_data_by_sorting_key(entries_list, sorting_key):
#     """Engine of sorting"""
#
#     if sorting_key['order_by'] in ['view_number', 'vote_number']:
#         # it is necessary to cast value to int to use function sort
#         for entry in entries_list:
#             entry[sorting_key['order_by']] = int(entry[sorting_key['order_by']])
#
#         new_list = sorted(entries_list, key=lambda k: k[sorting_key['order_by']],
#                           reverse=True if sorting_key['order_direction'] == 'desc' else False)
#     else:
#         new_list = sorted(entries_list, key=lambda k: k[sorting_key['order_by']].lower(),
#                           reverse=True if sorting_key['order_direction'] == 'desc' else False)
#     return [convert_timestamp(entry) for entry in new_list]
#
#
# def convert_timestamp(entry):
#     """Returns entry with human-friendly converted timestamp"""
#
#     time_stamp = int(entry["submission_time"])
#     converted_time = datetime.fromtimestamp(time_stamp)
#     entry["submission_time"] = converted_time
#
#     return entry
#
#
# def get_question_by_id(question_id, questions):
#     """Returns question (entry) of given id from list with converted timestamp"""
#
#     for question in questions:
#         if question["id"] == question_id:
#             return convert_timestamp(question)
#
#
# def get_question_by_id_without_timestamp_conversion(question_id, questions):
#     """As above but without timestamp convertion"""
#
#     for question in questions:
#         if question["id"] == question_id:
#             return question
#
#
# def get_entry_by_id(entry_id, entries_list):
#     """As above but without timestamp convertion"""
#
#     for entry in entries_list:
#         if entry['id'] == entry_id:
#             return entry
#
#
# def get_answers_for_question(question_id, answers):
#     """Returns list of answer entries for question of given id"""
#
#     question_answers = []
#     for answer in answers:
#         if answer["question_id"] == question_id:
#             question_answers.append(convert_timestamp(answer))
#
#     return question_answers
#
#
# def filter_data(dict_data, headers):
#     """Returns entry filtered by wished headers"""
#
#     filtered_data = []
#     try:
#         for entry in dict_data:
#             filtered_entry = {}
#             for header in headers:
#                 filtered_entry[header] = entry[header]
#             filtered_data.append(filtered_entry)
#
#         return filtered_data
#     # eliminate error occurring when empty dict_data filtered
#     except TypeError:
#         return []
#
#
# def get_next_id(entries_list):
#     """Computes next id based on given entries list."""
#
#     next_id = 0
#     for entry in entries_list:
#         entry_id = int(entry['id'])
#         if entry_id >= next_id:
#             next_id = entry_id
#
#     return next_id + 1
#
#
# def delete_rows(question_id, criteria, entries_list):
#     """Returns new list without deleted id entry. Services deletion of question and associated answers
#     and their images."""
#
#     temp_list = []
#
#     for entry in entries_list:
#         if entry[criteria] != question_id:
#             temp_list.append(entry)
#         else:
#             if entry['image'] != 'none.jpg':
#                 if criteria == 'id':
#                     sub_dir = 'questions'
#                 else:
#                     sub_dir = 'answers'
#                 data_handler.delete_image(entry['image'], sub_dir, entry['id'])
#
#     return temp_list
#
#
def get_current_timestamp():
    """Return current timestamp in seconds"""

    return int(time.time())
#
#
# def set_initial_values(entry_dictionary, listed_base_data):
#     """Set initial values for entry_dictionary based on database data (listed_base_data)"""
#
#     entry_dictionary['submission_time'] = str(get_current_timestamp())
#     entry_dictionary['vote_number'] = '0'
#     entry_dictionary['id'] = str(get_next_id(listed_base_data))
#
#
# def add_new_question(form_data, request_files):
#     """Engine of adding new question."""
#
#     questions = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)
#     requested_data = dict(form_data)
#
#     set_initial_values(requested_data, questions)
#     requested_data['view_number'] = '0'
#
#     image_filename = process_image_input(
#         request_files['image'],
#         'questions',
#         requested_data['id'])
#
#     requested_data['image'] = image_filename
#
#     questions.append(requested_data)
#     data_handler.write_file(data_handler.QUESTIONS_DATA_FILE_PATH, data_handler.QUESTIONS_DATA_HEADER, questions)
#     return requested_data['id']
#
#

#
#
def get_image_name(image_storage_obj):
    """Checks if storage object is not empty. If it is returns default image filename else returns object filename"""

    storage_obj_empty = image_storage_obj.filename == ""
    invalid_extension = ".jpg" not in image_storage_obj.filename and ".png" not in image_storage_obj.filename

    if storage_obj_empty or invalid_extension:
        image_name = 'none.jpg'
    else:
        data_handler.save_image(image_storage_obj, sub_dir, entry_id)
        image_name = image_storage_obj.filename

    return image_name
#
#
# def update_entry(updated_entry, entries_list):
#     """Updates entry in entries_list"""
#
#     for entry in entries_list:
#         if entry['id'] == updated_entry['id']:
#             entries_list[entries_list.index(entry)] = updated_entry
#
#
# def vote_on_post(entry_id, vote_value, entry_type):
#     """Engine for voting on any type of post on website."""
#
#     if entry_type == "question":
#         entries_list = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)
#     else:
#         entries_list = data_handler.read_file(data_handler.ANSWER_DATA_FILE_PATH)
#
#     entry = get_entry_by_id(entry_id, entries_list)
#
#     if vote_value == "vote_up":
#         entry["vote_number"] = str(int(entry["vote_number"]) + 1)
#     else:
#         entry["vote_number"] = str(int(entry["vote_number"]) - 1)
#
#     update_entry(entry, entries_list)
#
#     if entry_type == "answer":
#         data_handler.write_file(data_handler.ANSWER_DATA_FILE_PATH, data_handler.ANSWERS_DATA_HEADER, entries_list)
#         id_of_questions_to_redirect = entry['question_id']
#     else:
#         data_handler.write_file(data_handler.QUESTIONS_DATA_FILE_PATH, data_handler.QUESTIONS_DATA_HEADER, entries_list)
#         id_of_questions_to_redirect = entry_id
#
#     return id_of_questions_to_redirect
#
#
# def edit_entry(form_data, entry, entries_list):
#     """Engine for editing any type on post on website."""
#
#     entry['message'] = form_data['message']
#     entry['vote_number'] = '0'
#
#     if 'question_id' not in entry.keys():
#         entry['title'] = form_data['title']
#         database_path = data_handler.QUESTIONS_DATA_FILE_PATH
#         database_headers = data_handler.QUESTIONS_DATA_HEADER
#     else:
#         database_path = data_handler.ANSWER_DATA_FILE_PATH
#         database_headers = data_handler.ANSWERS_DATA_HEADER
#
#     update_entry(entry, entries_list)
#     data_handler.write_file(database_path, database_headers, entries_list)
#
#
# def delete_answer(answer_id):
#     """Deletes answer of given id from database."""
#
#     answers = data_handler.read_file(data_handler.ANSWER_DATA_FILE_PATH)
#     answer = get_entry_by_id(answer_id, answers)
#     redirection_id = answer['question_id']
#
#     del answers[answers.index(answer)]
#     data_handler.write_file(data_handler.ANSWER_DATA_FILE_PATH, data_handler.ANSWERS_DATA_HEADER, answers)
#
#     return redirection_id
#
#
#
#
