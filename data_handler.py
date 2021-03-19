import os
import pathlib

import psycopg2
import psycopg2.extras

UPLOADED_IMAGES_FILE_PATH = pathlib.Path(f"{pathlib.Path(__file__).parent.absolute()}/static/images")


def get_connection_string():

    user_name = os.environ.get('PSQL_USER_NAME')
    password = os.environ.get('PSQL_PASSWORD')
    host = os.environ.get('PSQL_HOST')
    database_name = os.environ.get('PSQL_DB_NAME')

    env_variables_defined = user_name and password and host and database_name

    if env_variables_defined:
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


def save_image(form_image, sub_dir, entry_id):

    path = UPLOADED_IMAGES_FILE_PATH / sub_dir / entry_id
    if not os.path.exists(path):
        os.makedirs(path)

    form_image.save(path / form_image.filename)


def delete_image(image_filename, sub_dir, entry_id):
    try:
        if image_filename != "none.jpg":

            entry_id = str(entry_id)
            path = UPLOADED_IMAGES_FILE_PATH / sub_dir / entry_id
            os.remove(UPLOADED_IMAGES_FILE_PATH / sub_dir / entry_id / image_filename)

            if len(os.listdir(path)) == 0:
                os.rmdir(path)

    except FileNotFoundError:
        return

