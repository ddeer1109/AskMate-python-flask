from psycopg2.extras import RealDictCursor
import data_handler


@data_handler.connection_handler
def get_all_tags(cursor: RealDictCursor):
    query = """
        SELECT * 
        FROM tag
    """

    cursor.execute(query)
    return cursor.fetchall()


@data_handler.connection_handler
def add_new_tag_to_db(cursor: RealDictCursor, tag):
    comment = """
        INSERT INTO tag(name) values(%(tag)s)
    """

    cursor.execute(comment, {'tag': tag})


@data_handler.connection_handler
def add_new_tag_to_question(cursor: RealDictCursor, question_id, tag_id):
    try:
        command = """
            INSERT INTO question_tag(question_id, tag_id) 
            VALUES(%(question_id)s, %(tag_id)s)
        """
        cursor.execute(command, {'question_id': question_id, 'tag_id': tag_id})
        return "tag has been added"
    except:
        return "current tag is already in question"


@data_handler.connection_handler
def remove_single_tag_from_question(cursor: RealDictCursor, question_id, tag_id):
    commend = """
        DELETE FROM question_tag
        WHERE question_id = %(question_id)s AND tag_id = %(tag_id)s
    """

    cursor.execute(commend, {'question_id': question_id, 'tag_id': tag_id})


@data_handler.connection_handler
def delete_question_tags(cursor: RealDictCursor, question_id):
    command = """
    DELETE FROM question_tag
    WHERE question_id = %(question_id)s
    """

    cursor.execute(command, {'question_id': question_id})


