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
def get_all_data_by_query(cursor: RealDictCursor, order_by, order_direction):
    query = f"""
        SELECT *
        FROM question
        ORDER By {order_by} {order_direction}
    """

    cursor.execute(query)
    return cursor.fetchall()


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
                ORDER BY submission_time
        """

    cursor.execute(query, {'question_id': question_id_int})
    return cursor.fetchall()

@data_handler.connection_handler
def get_tags_for_question(cursor: RealDictCursor, question_id):
    query = """
    SELECT name 
    FROM question_tag
    INNER JOIN tag
        ON question_tag.tag_id = tag.id
    WHERE question_id = %(question_id)s
    """

    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()

@data_handler.connection_handler
def get_all_tags(cursor: RealDictCursor):
    query = """
        SELECT name 
        FROM tag
    """

    cursor.execute(query)
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
    RETURNING id, question_id, image
    """

    cursor.execute(comment, {'id': answer_id})

    data_to_delete = cursor.fetchone()
    data_handler.delete_image(data_to_delete['image'], 'answers', data_to_delete['id'])

    return data_to_delete['question_id']


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


def get_current_timestamp():
    """Return current timestamp in seconds"""

    return int(time.time())


def get_image_name(image_storage_obj):
    """Checks if storage object is not empty. If it is returns default image filename else returns object filename"""

    storage_obj_empty = image_storage_obj.filename == ""
    invalid_extension = ".jpg" not in image_storage_obj.filename and ".png" not in image_storage_obj.filename

    if storage_obj_empty or invalid_extension:
        image_name = 'none.jpg'
    else:
        image_name = image_storage_obj.filename

    return image_name
#