from flask import render_template

from app_holder import app
from app_service_getters import *
from app_service_posts import *
from app_service_updates import *
from app_service_deletions import *


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)


