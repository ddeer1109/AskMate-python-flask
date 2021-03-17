from psycopg2.extras import RealDictCursor

import data_handler
import util
# from service_answer import get_answer
from service_user import add_user_comment_activity


@data_handler.connection_handler
def get_comment_by_id(cursor: RealDictCursor, comment_id):

    query = """SELECT * 
    FROM comment
    WHERE id=%(comment_id)s"""

    cursor.execute(query, {'comment_id': comment_id})

    return cursor.fetchone()


@data_handler.connection_handler
def add_comment(cursor: RealDictCursor, message, entry_type, entry_id, user_id):
    entry_column_name = 'question_id' if entry_type == 'question' else 'answer_id'
    submission_time = util.get_datetime_now()

    query = f"""
        INSERT INTO comment
        ({entry_column_name}, submission_time, message)
        VALUES (%(entry_id)s, %(submission_time)s, %(message)s)
        RETURNING id
    """

    cursor.execute(query, {'entry_id': entry_id, 'submission_time': submission_time, 'message': message})

    add_user_comment_activity(user_id, cursor.fetchone()['id'])



@data_handler.connection_handler
def delete_comment_by_id(cursor: RealDictCursor, comment_id: str):
    comment = """
    DELETE 
    from users_activity
    WHERE comment_id = %(id)s
    """
    cursor.execute(comment, {'id': comment_id})
    comment = """
    DELETE 
    FROM comment
    WHERE id=%(id)s
    RETURNING id, question_id, answer_id
    """

    cursor.execute(comment, {'id': comment_id})




@data_handler.connection_handler
def delete_comments_of_entry(cursor: RealDictCursor, entry_type, entry_id):

    entry_type_id = 'question_id' if entry_type == "question" else "answer_id"

    command = f"""
                   DELETE FROM users_activity 
                   WHERE comment_id in (SELECT id
                   FROM comment
                   WHERE {entry_type_id}=%(entry_id)s)
                   """
    cursor.execute(command, {'entry_id': entry_id})
    command = f"""
                   DELETE
                   FROM comment
                   WHERE {entry_type_id}=%(entry_id)s
                   """
    cursor.execute(command, {'entry_id': entry_id})



@data_handler.connection_handler
def update_comment(cursor: RealDictCursor, comment_id, message):

    command = """
    UPDATE comment 
    SET message=%(message)s
    WHERE id=%(comment_id)s
    RETURNING question_id, answer_id
    """

    cursor.execute(command, {'message': message, 'comment_id': comment_id})


