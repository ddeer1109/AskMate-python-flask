from psycopg2.extras import RealDictCursor
import data_handler
import util

#
#          ------>> GETTERS <<------
#


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
def get_answer(cursor: RealDictCursor, answer_id):
    query = """
        SELECT id, question_id, message FROM answer
        WHERE id = %(answer_id)s
    """
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


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
    # question_id = int(id_string)

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
def get_comment_by_id(cursor: RealDictCursor, comment_id):

    query = """SELECT * 
    FROM comment
    WHERE id=%(comment_id)s"""

    cursor.execute(query, {'comment_id': comment_id})

    return cursor.fetchone()


@data_handler.connection_handler
def get_all_tags(cursor: RealDictCursor):
    query = """
        SELECT * 
        FROM tag
    """

    cursor.execute(query)
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

#
#          ------>> INSERTS <<------
#

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
def add_new_entry(cursor: RealDictCursor, table_name: str, form_data=None, request_files=None, question_id=None, user_id=None):

    complete_dict_data = util.init_complete_dict_entry(table_name, form_data, request_files, question_id)

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

    # if table_name == 'question':
    return entry_id


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

    if entry_type == 'question':
        return entry_id
    else:
        return get_answer(entry_id)['question_id']




#
#          ------>> DELETIONS <<------
#


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

    return data_to_delete['question_id']


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

    ids = cursor.fetchone()

    if ids['question_id'] is not None:
        return ids['question_id']
    else:
        answer = get_answer(ids['answer_id'])
        return answer['question_id']


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
def vote_on_post(cursor: RealDictCursor, entry_id, vote_value, entry_type):
    params = {'entry_id': entry_id}
    if entry_type == 'answer':
        returning_string = "RETURNING question_id"
    elif entry_type == 'question':
        returning_string = "RETURNING id"

    if vote_value == 'vote_up':
        params['vote'] = + 1
    else:
        params['vote'] = - 1

    comment = f"""
    UPDATE {entry_type}
    SET vote_number = vote_number + %(vote)s
    WHERE id=%(entry_id)s
    {returning_string} as redirect_id"""

    cursor.execute(comment, params)
    return cursor.fetchone()['redirect_id']


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
    redirect_id = vote_on_post(entry_id, vote_value, entry_type)

    command = f"""
    DELETE FROM users_votes
    WHERE {entry_type}_id = %(entry_id)s
    """
    cursor.execute(command, {'entry_id': entry_id})
    return redirect_id


@data_handler.connection_handler
def update_comment(cursor: RealDictCursor, comment_id, message):

    command = """
    UPDATE comment 
    SET message=%(message)s
    WHERE id=%(comment_id)s
    RETURNING question_id, answer_id
    """

    cursor.execute(command, {'message': message, 'comment_id': comment_id})
    ids = cursor.fetchone()

    if ids['question_id'] is not None:
        return ids['question_id']
    else:
        answer = get_answer(ids['answer_id'])
        return answer['question_id']


@data_handler.connection_handler
def update_views_count(cursor: RealDictCursor, question_id):
    command = """
    UPDATE question
    SET view_number = view_number + 1
    WHERE id = %(question_id)s
    """

    cursor.execute(command, {'question_id': question_id})


#==================== CLIENT
def is_authenticated(login, password):
    return is_existing_user(login) and is_password_ok(login, password)

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

    return util.check_password(password, hashed_password)


def process_registration(login, password):
    if is_existing_user(login):
        return "Login is not available"

    password = util.hash_given_password(password)
    create_new_user(login, password)

    return ""


@data_handler.connection_handler
def create_new_user(cursor: RealDictCursor, login, password):
    registration_time = util.get_datetime_now()

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
