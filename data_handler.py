# import csv
# import os
import pathlib

# Creates a decorator to handle the database connection/cursor opening/closing.
# Creates the cursor with RealDictCursor, thus it returns real dictionaries, where the column names are the keys.
import os

import psycopg2
import psycopg2.extras


def get_connection_string():
    # setup connection string
    # to do this, please define these environment variables first
    user_name = os.environ.get('PSQL_USER_NAME')
    password = os.environ.get('PSQL_PASSWORD')
    host = os.environ.get('PSQL_HOST')
    database_name = os.environ.get('PSQL_DB_NAME')

    env_variables_defined = user_name and password and host and database_name

    if env_variables_defined:
        # this string describes all info for psycopg2 to connect to the database
        return 'postgresql://{user_name}:{password}@{host}/{database_name}'.format(
            user_name=user_name,
            password=password,
            host=host,
            database_name=database_name
        )
    else:
        raise KeyError('Some necessary environment variable(s) are not defined')


def open_database():
    try:
        connection_string = get_connection_string()
        connection = psycopg2.connect(connection_string)
        connection.autocommit = True
    except psycopg2.DatabaseError as exception:
        print('Database connection problem')
        raise exception
    return connection


def connection_handler(function):
    def wrapper(*args, **kwargs):
        connection = open_database()
        # we set the cursor_factory parameter to return with a RealDictCursor cursor (cursor which provide dictionaries)
        dict_cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        ret_value = function(dict_cur, *args, **kwargs)
        dict_cur.close()
        connection.close()
        return ret_value

    return wrapper


#
# QUESTIONS_DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/question.csv"
# ANSWER_DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/answer.csv"
# QUESTIONS_DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
# ANSWERS_DATA_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']
#
UPLOADED_IMAGES_FILE_PATH = pathlib.Path(f"{pathlib.Path(__file__).parent.absolute()}/static/images")
#
#
# def write_file(path, header, dictionaries_list):
#     with open(path, 'w', newline='') as csv_file:
#         csv_writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=',', quotechar='"')
#         csv_writer.writeheader()
#         csv_writer.writerows(dictionaries_list)
#
#
# def read_file(path):
#     dictionaries_list = []
#     with open(path) as csv_file:
#         csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
#         for row in csv_reader:
#             dictionaries_list.append(row)
#
#         return dictionaries_list
#
#


def save_image(form_image, sub_dir, entry_id):

    path = UPLOADED_IMAGES_FILE_PATH / sub_dir / entry_id
    if not os.path.exists(path):
        os.makedirs(path)

    form_image.save(path / form_image.filename)


def delete_image(image_filename, sub_dir, entry_id):
    entry_id = str(entry_id)
    path = UPLOADED_IMAGES_FILE_PATH / sub_dir / entry_id
    os.remove(UPLOADED_IMAGES_FILE_PATH / sub_dir / entry_id / image_filename)

    if len(os.listdir(path)) == 0:
        os.rmdir(path)

