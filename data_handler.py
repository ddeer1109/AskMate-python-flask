from typing import List, Dict

from psycopg2 import sql
from psycopg2.extras import RealDictCursor

import database_common


@database_common.connection_handler
def get_mentors(cursor: RealDictCursor) -> list:
    query = """
        SELECT first_name, last_name, city
        FROM mentor
        ORDER BY first_name"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_mentors_by_last_name(cursor: RealDictCursor, last_name: str) -> list:
    query = """
        SELECT first_name, last_name, city
        FROM mentor
        WHERE  last_name
        ORDER BY first_name"""
    cursor.execute(query)
    return cursor.fetchall()

@database_common.connection_handler
def get_mentors_by_city(cursor: RealDictCursor, city: str) -> list:
    query = """
        SELECT first_name, last_name, city
        FROM mentor
        WHERE city ILIKE $(city)s
        ORDER BY first_name"""
    cursor.execute(query, {'city': city})
    return cursor.fetchall()

@database_common.connection_handler
def get_applicant_data_by_name(cursor: RealDictCursor, name: str):
    query = """
            SELECT first_name, last_name, phone_number
            FROM applicant
            WHERE first_name ILIKE %(name)s OR last_name ILIKE %(name)s
            ORDER BY first_name"""
    cursor.execute(query, {'name': name})
    return cursor.fetchall()


@database_common.connection_handler
def get_applicant_data_by_email_ending(cursor: RealDictCursor, email_ending: str):
    email_ending = "%" + email_ending

    query = """
                SELECT first_name, last_name, phone_number
                FROM applicant
                WHERE city LIKE %(email_ending)s OR first_name ILIKE %(name)s
                ORDER BY first_name"""
    cursor.execute(query, {'email_ending': email_ending})
    return cursor.fetchall()

@database_common.connection_handler
def get_applicants(cursor: RealDictCursor) -> list:
    query = """
        SELECT *
        FROM applicant
        ORDER BY first_name"""
    cursor.execute(query)
    return cursor.fetchall()

@database_common.connection_handler
def get_applicant_data_by_appcode(cursor: RealDictCursor, app_code: str):
    query = """
                SELECT *
                FROM applicant
                WHERE application_code=%(app_code)s
                ORDER BY first_name"""

    cursor.execute(query, {'app_code': app_code})
    return cursor.fetchone()

@database_common.connection_handler
def update_applicant_phone_number(cursor: RealDictCursor, code: int,  application_phone: str):
    query = """
                UPDATE applicant
                SET phone_number = %(new_number)s
                WHERE application_code=%(app_code)s
                """

    cursor.execute(query, {'new_number': application_phone, 'app_code': code})
    return True

@database_common.connection_handler
def delete_applicant(cursor: RealDictCursor, code: int):
    query = """
                DELETE FROM applicant
                WHERE application_code=%(app_code)s
                """

    cursor.execute(query, {'app_code': code})
    return True


############################################################################
import csv
import os
import pathlib


QUESTIONS_DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/question.csv"
ANSWER_DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/answer.csv"
QUESTIONS_DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_DATA_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']

UPLOADED_IMAGES_FILE_PATH = pathlib.Path(f"{pathlib.Path(__file__).parent.absolute()}/static/images")


def write_file(path, header, dictionaries_list):
    with open(path, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=header, delimiter=',', quotechar='"')
        csv_writer.writeheader()
        csv_writer.writerows(dictionaries_list)


def read_file(path):
    dictionaries_list = []
    with open(path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for row in csv_reader:
            dictionaries_list.append(row)

        return dictionaries_list


def save_image(form_image, sub_dir, entry_id):

    path = UPLOADED_IMAGES_FILE_PATH / sub_dir / entry_id
    if not os.path.exists(path):
        os.makedirs(path)

    form_image.save(path / form_image.filename)


def delete_image(image_filename, sub_dir, entry_id):
    path = UPLOADED_IMAGES_FILE_PATH / sub_dir / entry_id
    os.remove(UPLOADED_IMAGES_FILE_PATH / sub_dir / entry_id / image_filename)

    if len(os.listdir(path)) == 0:
        os.rmdir(path)

