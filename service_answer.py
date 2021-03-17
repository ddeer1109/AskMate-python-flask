from psycopg2.extras import RealDictCursor

import data_handler
from service_comment import delete_comments_of_entry
from service_user import delete_user_activities


@data_handler.connection_handler
def get_answer(cursor: RealDictCursor, answer_id):
    query = """
        SELECT id, question_id, message FROM answer
        WHERE id = %(answer_id)s
    """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


@data_handler.connection_handler
def get_answers_for_question(cursor: RealDictCursor, question_id_int: int):

    query = """
                SELECT 
                id, 
                submission_time as post_time, 
                vote_number as votes, 
                message, 
                image
                FROM answer
                WHERE question_id=%(question_id)s
                ORDER BY post_time
        """

    cursor.execute(query, {'question_id': question_id_int})

    answers = cursor.fetchall()
    for answer in answers:
        answer['comments'] = get_comments_for_answer(answer['id'])

    return answers


@data_handler.connection_handler
def get_comments_for_answer(cursor: RealDictCursor, answer_id):

    query = """
        SELECT id, submission_time as post_time, message, edited_count 
        FROM comment
        WHERE answer_id=%(answer_id)s
    """

    cursor.execute(query, {'answer_id': answer_id})
    comments = cursor.fetchall()
    return comments


@data_handler.connection_handler
def delete_answers_by_question_id(cursor: RealDictCursor, question_id):

    question_answers = get_answers_for_question(question_id)
    for answer in question_answers:
        delete_comments_of_entry(entry_type="answer", entry_id=answer['id'])
        delete_user_activities(answer['id'], "answer")

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
def delete_answer_by_id(cursor: RealDictCursor, answer_id: str):

    delete_comments_of_entry(entry_type="answer", entry_id=answer_id)
    delete_user_activities(answer_id, "answer")

    comment = """
    DELETE 
    FROM answer
    WHERE id=%(id)s
    RETURNING id, question_id, image
    """

    cursor.execute(comment, {'id': answer_id})

    data_to_delete = cursor.fetchone()
    data_handler.delete_image(data_to_delete['image'], 'answers', data_to_delete['id'])


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
