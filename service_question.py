from psycopg2.extras import RealDictCursor

import data_handler
import util
from service_answer import delete_answers_by_question_id
from service_comment import delete_comments_of_entry
from service_tag import delete_question_tags
from service_user import delete_user_activities


@data_handler.connection_handler
def get_five_questions(cursor: RealDictCursor) -> list:
    query = """
            SELECT id, submission_time as post_time, title, message, image
            FROM question
            ORDER BY post_time DESC
            LIMIT 5"""

    cursor.execute(query)
    data = cursor.fetchall()
    return data


@data_handler.connection_handler
def get_all_data(cursor: RealDictCursor) -> list:

    query = """
        SELECT *
        FROM question
        ORDER BY submission_time DESC"""

    cursor.execute(query)
    questions = cursor.fetchall()
    util.add_answer_snippets(questions)
    return questions


@data_handler.connection_handler
def get_all_data_by_query(cursor: RealDictCursor, order_by, order_direction):
    query = f"""
        SELECT *
        FROM question
        ORDER By {order_by} {order_direction}
    """

    cursor.execute(query)
    questions = cursor.fetchall()
    util.add_answer_snippets(questions)

    return questions

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
def get_question_by_id(cursor: RealDictCursor, id_string: str):

    query = """
            SELECT 
            id, 
            submission_time as post_time,
            view_number as views, 
            vote_number as votes, 
            title, 
            message, 
            image
            FROM question
            WHERE id=%(question_id)s
    """

    cursor.execute(query, {'question_id': id_string})
    return cursor.fetchone()


@data_handler.connection_handler
def get_tags_for_question(cursor: RealDictCursor, question_id):
    query = """
    SELECT id, name 
    FROM question_tag
    INNER JOIN tag
        ON question_tag.tag_id = tag.id
    WHERE question_id = %(question_id)s
    """
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@data_handler.connection_handler
def get_comments_for_question(cursor: RealDictCursor, question_id_int: int):
    query = """
                    SELECT id, submission_time as post_time, message, edited_count 
                    FROM comment
                    WHERE question_id=%(question_id)s
            """

    cursor.execute(query, {'question_id': question_id_int})
    return cursor.fetchall()


@data_handler.connection_handler
def get_entries_by_search_phrase(cursor: RealDictCursor, search_phrase):
    original_phrase = search_phrase
    search_phrase = "%" + search_phrase + "%"

    query = """
    SELECT DISTINCT * 
    FROM question 
    WHERE (LOWER(title) LIKE LOWER(%(search_phrase)s)) 
    or (LOWER(message) LIKE LOWER(%(search_phrase)s))
    """

    cursor.execute(query, {'search_phrase': search_phrase})

    questions = cursor.fetchall()

    util.highlight_search_phrases_in_lists(questions, original_phrase)
    util.add_answer_snippets(questions)

    query = """
    SELECT 
    answer.question_id AS id, question.submission_time, question.view_number, 
    question.vote_number, question.title, question.message, question.image
    FROM question
    INNER JOIN answer
    ON answer.question_id = question.id
    WHERE LOWER(answer.message) LIKE LOWER(%(search_phrase)s)
    """

    cursor.execute(query, {'search_phrase': search_phrase})

    questions_with_answers = cursor.fetchall()

    util.add_answer_snippets(questions_with_answers)
    util.highlight_search_phrases_in_lists(questions_with_answers, original_phrase, answers=True)
    util.process_phrase_searched_in_both_question_and_answer(questions, questions_with_answers)

    return questions, questions_with_answers


@data_handler.connection_handler
def delete_question(cursor: RealDictCursor, question_id: str):

    delete_user_activities(question_id, "question")
    delete_comments_of_entry(entry_type="question", entry_id=question_id)
    delete_answers_by_question_id(question_id)
    delete_question_tags(question_id)

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
def save_edited_question(cursor: RealDictCursor, question_id, title, message):
    comment = """
        UPDATE question
        SET title = %(title)s, message = %(message)s
        WHERE id = %(question_id)s
    """

    cursor.execute(comment, {'question_id': question_id, 'title': title, 'message': message})


@data_handler.connection_handler
def update_views_count(cursor: RealDictCursor, question_id):
    command = """
    UPDATE question
    SET view_number = view_number + 1
    WHERE id = %(question_id)s
    """

    cursor.execute(command, {'question_id': question_id})


