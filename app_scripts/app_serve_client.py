from app_holder import *
from data_management_scripts import client_manager as client, service_user as usr


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def post_login():
    login = request.form['login']
    password = request.form['password']

    if usr.is_authenticated(login, password):
        user = usr.get_users_session_data(login)
        client.set_session(user['login'], user['id'])

        return redirect(url_for('get_five_question'))

    return render_template('login.html', message="Incorrect Login or Password")


@app.route('/logout')
def logout():
    client.drop_session()
    return redirect(url_for('get_five_question'))


@app.route('/registration')
def display_registration():
    return render_template('registration.html')


@app.route('/registration', methods=['POST'])
def registration():
    login = request.form.get('login')
    password = request.form.get('password')

    response = client.process_registration(login, password)

    if response:
        return render_template('registration.html', message=response)
    else:
        return render_template('login.html', registration_message="You've been registered")

