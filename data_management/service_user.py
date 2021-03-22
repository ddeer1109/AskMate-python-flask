from psycopg2.extras import RealDictCursor

import data_handler
from data_management.util import get_datetime_now, check_password


@data_handler.connection_handler
def get_users_session_data(cursor: RealDictCursor, login):
    query = """
        SELECT id, login
        FROM users
        WHERE login=%(login)s
    """

    cursor.execute(query, {'login': login})
    user = cursor.fetchone()
    return user


@data_handler.connection_handler
def get_users(cursor: RealDictCursor):
    query = """
    SELECT users.id AS id, users.login AS Login,
    users.registration_date AS Registration_Date,
    users_statistics.question_count AS Question_Count, 
    users_statistics.answer_count AS Answers_Count,
    users_statistics.comment_count AS Comment_Count,
    users_statistics.reputation_value AS Reputation
    FROM users
    INNER JOIN users_statistics
    ON users.id = users_statistics.user_id
    ORDER BY Registration_Date
    """

    cursor.execute(query)
    return cursor.fetchall()

@data_handler.connection_handler
def get_user_data(cursor: RealDictCursor, user_id):
    query = """
        SELECT u.login, u.registration_date, us.question_count, 
            us.answer_count, us.comment_count, us.reputation_value
        FROM users as u
        INNER JOIN users_statistics as us
            ON u.id = us.user_id
        WHERE u.id=%(user_id)s
    """

    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchone()

@data_handler.connection_handler
def get_questions_of_user(cursor: RealDictCursor, user_id):
    query ="""
        SELECT qst.* FROM question as qst
        INNER JOIN users_activity as act
            ON qst.id = act.question_id
        WHERE act.user_id = %(user_id)s
    """

    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()

@data_handler.connection_handler
def get_answers_of_user(cursor: RealDictCursor, user_id):
    query = """
        SELECT ans.* FROM answer as ans
        INNER JOIN users_activity as act
            ON ans.id = act.answer_id
        WHERE act.user_id = %(user_id)s
    """

    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@data_handler.connection_handler
def get_comments_of_user(cursor: RealDictCursor, user_id):
    query = """
            SELECT com.* FROM comment as com
            INNER JOIN users_activity as act
                ON com.id = act.comment_id
            WHERE act.user_id = %(user_id)s
        """

    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@data_handler.connection_handler
def get_user_post(cursor: RealDictCursor, user_id, post_id, post_type):
    column_name = post_type + "_id"
    query = f"""
        SELECT user_id, {column_name}
        FROM users_activity
        WHERE user_id=%(user_id)s AND {column_name}=%(post_id)s
    """

    cursor.execute(query, {'user_id': user_id, 'post_id': post_id})
    return cursor.fetchone()


@data_handler.connection_handler
def create_new_user(cursor: RealDictCursor, login, password):
    registration_time = get_datetime_now()

    command = f"""
        INSERT INTO users
        (login, password, registration_date)
        VALUES (%(login)s, %(password)s, %(registration_time)s)
        RETURNING id

    """

    cursor.execute(command, {'login': login, 'registration_time': registration_time, 'password': str(password)[2:-1]})
    new_user_id = cursor.fetchone()['id']

    query = f"""
        INSERT INTO users_statistics
        (user_id, question_count, answer_count, comment_count, reputation_value)
        VALUES (%(new_user_id)s, 1, 1, 1, 1)
    """
    cursor.execute(query, {'new_user_id': new_user_id})

    # TODO - improve password management, bytes etc.


def is_authenticated(login, password):
    return is_existing_user(login) and is_password_ok(login, password)


@data_handler.connection_handler
def is_existing_user(cursor: RealDictCursor, login):
    query = """
        SELECT login 
        FROM users
        WHERE login=%(login)s
    """

    cursor.execute(query, {'login': login})
    return bool(cursor.fetchone())


@data_handler.connection_handler
def is_password_ok(cursor: RealDictCursor, login, password):
    query = """
        SELECT password
        FROM users
        WHERE login=%(login)s
    """

    cursor.execute(query, {'login': login, 'password': password})
    hashed_password = cursor.fetchone()['password']

    return check_password(password, hashed_password)


@data_handler.connection_handler
def add_user_answer_activity(cursor: RealDictCursor,  user_id, answer_id):
    command = """
            INSERT INTO users_activity(user_id, answer_id)
            VALUES (%(user_id)s, %(answer_id)s)
        """

    cursor.execute(command, {'user_id': user_id, 'answer_id': answer_id})


@data_handler.connection_handler
def add_user_question_activity(cursor: RealDictCursor, user_id, question_id):
    command = """
        INSERT INTO users_activity(user_id, question_id)
        VALUES (%(user_id)s, %(question_id)s)
    """

    cursor.execute(command, {'user_id': user_id, 'question_id': question_id})


@data_handler.connection_handler
def add_user_comment_activity(cursor: RealDictCursor, user_id, comment_id):
    command = """
            INSERT INTO users_activity(user_id, comment_id)
            VALUES (%(user_id)s, %(comment_id)s)
        """

    cursor.execute(command, {'user_id': user_id, 'comment_id': comment_id})


@data_handler.connection_handler
def delete_user_activities(cursor: RealDictCursor, entry_id, type_of_entry):
    column_name = type_of_entry + "_id"
    if type_of_entry in ['question', 'answer']:
        votes_delete_query = f"""
                DELETE from users_votes
                WHERE {column_name} = %(entry_id)s;"""

    else:
        votes_delete_query = ""

    command = f"""DELETE from users_activity
                WHERE {column_name} = %(entry_id)s;
                {votes_delete_query}
    """
    cursor.execute(command, {'entry_id': entry_id})

    command = f"""
        DELETE from users_activity
        WHERE {column_name} = %(entry_id)s;
        """

    cursor.execute(command, {'entry_id': entry_id})


@data_handler.connection_handler
def get_user_vote(cursor: RealDictCursor, user_id, entry_id_tuple):
    column_name, entry_id = entry_id_tuple[0], entry_id_tuple[1]
    query = f"""
    SELECT * FROM users_votes
    WHERE user_id = %(user_id)s 
    AND {column_name} = %(entry_id)s
    """
    cursor.execute(query, {'user_id': user_id, 'entry_id': entry_id})

    return cursor.fetchone()

#==================== CLIENT
