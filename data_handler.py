import csv
import os
import pathlib


QUESTIONS_DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/question.csv"
ANSWER_DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else f"{pathlib.Path(__file__).parent.absolute()}/sample_data/answer.csv"
QUESTIONS_DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_DATA_HEADER = ['id', 'submission_time', 'vote_number', 'message', 'image']
ANSWERS_DATA_HEADER_FILE = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']

def save_all_questions(question):
    with open(QUESTIONS_DATA_FILE_PATH, 'a', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=QUESTIONS_DATA_HEADER, delimiter=',', quotechar='"')
        csv_writer.writerow(question)

def get_all_questions():
    questions = []

    with open(QUESTIONS_DATA_FILE_PATH) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for row in csv_reader:
            questions.append(row)

        return questions


def get_all_answers():
    answers = []

    with open(ANSWER_DATA_FILE_PATH) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
        for row in csv_reader:
            answers.append(row)
        return answers
print(get_all_answers())

# def get_all_answers():
#     answers = []
#
#     with open(ANSWER_DATA_FILE_PATH) as csv_file:
#         csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='"')
#         for row in csv_reader:
#             answers.append(row)
#         print(answers)
#         return answers
# get_all_answers()
# print(get_all_answers())


def get_data(PATH, FILENAME, data):
    with open(PATH + '/sample_data/' + FILENAME, 'r') as csv_file:
            data = csv.reader(csv_file)
            rows = list(data)
    return rows


def save_all_answers(answers):
    with open(ANSWER_DATA_FILE_PATH, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=ANSWERS_DATA_HEADER_FILE, delimiter=',', quotechar='"')
        csv_writer.writeheader()
        csv_writer.writerows(answers)
        # for answer in answers:
        #     csv_writer.writerow(answer)

def save_all_questions(questions):
    with open(QUESTIONS_DATA_FILE_PATH, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=QUESTIONS_DATA_HEADER, delimiter=',', quotechar='"')
        csv_writer.writeheader()
        csv_writer.writerows(questions)



def save_single_answer(answer):
    with open(ANSWER_DATA_FILE_PATH, 'a', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=ANSWERS_DATA_HEADER_FILE, delimiter=',', quotechar='"')
        csv_writer.writerow(answer)

# here found bug - ANSWER_DATA_FILE_PATH instead of QUESTION_...
def save_single_question(question):
    with open(QUESTIONS_DATA_FILE_PATH, 'a', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=QUESTIONS_DATA_HEADER, delimiter=',', quotechar='"')
        csv_writer.writerow(question)
        print(question)
