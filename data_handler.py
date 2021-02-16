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


def save_image(form_image):
    path = UPLOADED_IMAGES_FILE_PATH / form_image.filename
    form_image.save(path)

