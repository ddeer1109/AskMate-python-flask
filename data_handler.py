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

