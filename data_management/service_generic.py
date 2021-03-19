from psycopg2.extras import RealDictCursor
import data_handler

from data_management.service_answer import get_answer
from data_management.service_comment import get_comment_by_id
from data_management.service_user import add_user_answer_activity, add_user_question_activity
from data_management.util import init_complete_dict_entry


def get_question_id_from_entry(entry_type, entry_id):
    if entry_type == 'question':
        return entry_id

    elif entry_type == 'comment':
        qst_id = get_comment_by_id(entry_id).get('question_id', None)
        ans_id = get_comment_by_id(entry_id).get('answer_id', None)

        if qst_id is not None:
            return qst_id
        else:
            return get_answer(ans_id)['question_id']

    else:
        return get_answer(entry_id)['question_id']


@data_handler.connection_handler
def add_new_entry(cursor: RealDictCursor, table_name: str, form_data=None, request_files=None, question_id=None, user_id=None):

    complete_dict_data = init_complete_dict_entry(table_name, form_data, request_files, question_id)

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

    if table_name == 'answer':
        add_user_answer_activity(user_id, entry_id)
    else:
        add_user_question_activity(user_id, entry_id)

    if request_files['image'].filename:

        if table_name == 'question':
            data_handler.save_image(request_files['image'], 'questions', entry_id)
        elif table_name == 'answer':
            data_handler.save_image(request_files['image'], 'answers', entry_id)

    return entry_id


@data_handler.connection_handler
def vote_on_post(cursor: RealDictCursor, entry_id, vote_value, entry_type):
    params = {'entry_id': entry_id}

    if vote_value == 'vote_up':
        params['vote'] = + 1
    else:
        params['vote'] = - 1

    comment = f"""
    UPDATE {entry_type}
    SET vote_number = vote_number + %(vote)s
    WHERE id=%(entry_id)s"""

    cursor.execute(comment, params)


@data_handler.connection_handler
def add_vote(cursor: RealDictCursor, user_id, vote_value, question_id=None, answer_id=None):
    column = "question_id" if question_id else "answer_id"
    entry_id = question_id if column == 'question_id' else answer_id
    command = f"""
    INSERT INTO users_votes(user_id, {column}, vote_value)
    VALUES (%(user_id)s, %(entry_id)s, %(vote_value)s)
    """
    cursor.execute(command, {'user_id': user_id, 'entry_id': entry_id, 'vote_value': vote_value})


@data_handler.connection_handler
def clear_vote(cursor: RealDictCursor, user_vote):
    vote_value = -user_vote.get('vote_value')
    vote_value = "vote_up" if vote_value == 1 else "vote_down"

    if user_vote.get('answer_id', None) is not None:
        entry_type = 'answer'
    elif user_vote.get('question_id', None) is not None:
        entry_type = 'question'

    entry_id = user_vote.get(f"{entry_type}_id")
    vote_on_post(entry_id, vote_value, entry_type)

    command = f"""
    DELETE FROM users_votes
    WHERE {entry_type}_id = %(entry_id)s
    """
    cursor.execute(command, {'entry_id': entry_id})

