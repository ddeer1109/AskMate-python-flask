from psycopg2.extras import RealDictCursor

import data_handler

from data_management.service_answer import delete_answers_by_question_id, get_answers_for_question
from data_management.service_comment import delete_comments_of_entry
from data_management.service_tag import delete_question_tags
from data_management.service_user import delete_user_activities
from data_management.util import highlight_search_phrases_in_lists, \
    process_phrase_searched_in_both_question_and_answer


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
    add_answer_snippets(questions)
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
    add_answer_snippets(questions)

    return questions


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
def get_comments_for_question(cursor: RealDictCursor, question_id_int: int):
    query = """
                    SELECT id, submission_time as post_time, message, edited_count 
                    FROM comment
                    WHERE question_id=%(question_id)s
            """

    cursor.execute(query, {'question_id': question_id_int})
    return cursor.fetchall()


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


def get_entries_by_search_phrase(search_phrase):
    questions_with_phrase_in_self = get_questions_with_searched_phrase(search_phrase)
    add_answer_snippets(questions_with_phrase_in_self)

    highlight_search_phrases_in_lists(
        questions_with_phrase_in_self,
        search_phrase)

    questions_with_phrase_in_answer = get_questions_with_searched_phrase_in_answers(search_phrase)
    add_answer_snippets(questions_with_phrase_in_answer)

    highlight_search_phrases_in_lists(
        questions_with_phrase_in_answer,
        search_phrase,
        answers=True)

    process_phrase_searched_in_both_question_and_answer(questions_with_phrase_in_self,
                                                        questions_with_phrase_in_answer)

    return questions_with_phrase_in_self, questions_with_phrase_in_answer


@data_handler.connection_handler
def get_questions_with_searched_phrase(cursor: RealDictCursor, search_phrase):
    search_phrase = "%" + search_phrase + "%"

    query = """
        SELECT DISTINCT id, submission_time as post_time, view_number, 
        vote_number, title, message, image
        FROM question 
        WHERE (LOWER(title) LIKE LOWER(%(search_phrase)s)) 
        or (LOWER(message) LIKE LOWER(%(search_phrase)s))
        """

    cursor.execute(query, {'search_phrase': search_phrase})
    questions = cursor.fetchall()

    return questions


@data_handler.connection_handler
def get_questions_with_searched_phrase_in_answers(cursor: RealDictCursor, search_phrase):
    query = """
        SELECT ans.question_id AS id, qst.submission_time as post_time, qst.view_number, 
        qst.vote_number, qst.title, qst.message, qst.image
        FROM question as qst
        INNER JOIN answer as ans
            ON ans.question_id = qst.id
            WHERE LOWER(ans.message) LIKE LOWER(%(search_phrase)s)
        """

    cursor.execute(query, {'search_phrase': search_phrase})
    questions_with_answers = cursor.fetchall()

    return questions_with_answers


def add_answer_snippets(questions_list):

    for question in questions_list:
        question['answers'] = get_answers_for_question(question['id'])


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


