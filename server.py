from flask import Flask
from data_handler import get_all_questions

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!!!"

@app.route("/list")
def get_list_of_questions():
    questions_list = get_all_questions()
    print(questions_list)

    return "list"


if __name__ == "__main__":
    app.run()