import csv
import os
import sample_data

DATA_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'sample_data\question.csv'
DATA_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']

def get_all_questions():
    questions = []

    with open(DATA_FILE_PATH) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='|')
        for row in csv_reader:
            questions.append(row)

        print(questions)
        return questions

get_all_questions()

