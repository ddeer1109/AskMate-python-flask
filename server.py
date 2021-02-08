from flask import Flask, render_template, request, redirect, url_for
from data_handler import get_all_questions, sort_questions_by_time

app = Flask(__name__)


# @app.route("/")
# def hello():
#     return "Hello World!!!"

@app.route("/")
@app.route("/list")
def get_list_of_questions():
    # questions = get_all_questions()
    questions = sort_questions_by_time()
    return render_template('list.html', questions=questions)


if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)