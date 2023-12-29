import os
import csv
import subprocess
from io import StringIO
from functools import wraps
from datetime import datetime

from flask import Flask, redirect, render_template, flash, jsonify, request, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from requests import get
import yadisk

from apscheduler.schedulers.background import BackgroundScheduler

import data
from data import db_session
from data.users import User
from forms.login import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['JSON_AS_ASCII'] = False
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    session.close()
    return user


def operator_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role_id != 1:
            return redirect('/login')
        return func(*args, **kwargs)

    return decorated_view


@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.login == form.username.data).first()
        session.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/profile')
        flash("Invalid username/password", 'error')

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect('/login')


@app.route('/profile')
@login_required
def profile():
    session = db_session.create_session()
    role_name = session.query(data.roles.Role).filter(current_user.role_id == data.roles.Role.id).first().name
    classes = []
    if role_name == 'professor':
        professor_id = session.query(data.professors.Professor) \
            .filter(data.professors.Professor.user_id == current_user.id).first().id
        classes = get(f"http://127.0.0.1:5000/classes/{professor_id}/0/0/0").json()
    if role_name == 'student':
        group_id = session.query(data.students.Student) \
            .filter(data.students.Student.user_id == current_user.id).first().group_id
        classes = get(f"http://127.0.0.1:5000/classes/0/0/{group_id}/0").json()
    session.close()
    return render_template('profile.html', title='Профиль', role_name=role_name, classes=classes)


@app.route('/classes/<int:professor_id>/<int:classroom_id>/<int:group_id>/<int:to_csv>', methods=['GET'])
def get_classes(professor_id=0, classroom_id=0, group_id=0, to_csv=0):
    session = db_session.create_session()
    query = session.query(data.classes.Class).order_by(data.classes.Class.weekday, data.classes.Class.class_number,
                                                       data.classes.Class.week_parity, data.classes.Class.group_id)

    if professor_id:
        query = query.filter_by(professor_id=professor_id)
    if classroom_id:
        query = query.filter_by(classroom_id=classroom_id)
    if group_id:
        query = query.filter_by(group_id=group_id)

    classes = query.all()

    class_list = []
    for class_instance in classes:
        professor = session.query(data.professors.Professor) \
            .filter(class_instance.professor_id == data.professors.Professor.id).first().name
        classroom = session.query(data.classrooms.Classroom) \
            .filter(class_instance.classroom_id == data.classrooms.Classroom.id).first().name
        group = session.query(data.groups.Group) \
            .filter(class_instance.group_id == data.groups.Group.id).first().name
        subject = session.query(data.subjects.Subject) \
            .filter(class_instance.subject_id == data.subjects.Subject.id).first().name

        weekdays = {
            1: 'Понедельник',
            2: 'Вторник',
            3: 'Среда',
            4: 'Четверг',
            5: 'Пятница',
            6: 'Суббота',
            7: 'Воскресенье'
        }
        class_dict = {
            'id': class_instance.id,
            'start': str(class_instance.start),
            'end': str(class_instance.end),
            'class_number': class_instance.class_number,
            'weekday': weekdays[class_instance.weekday],
            'week_parity': class_instance.week_parity,
            'subject': subject,
            'professor': professor,
            'classroom': classroom,
            'group': group
        }
        class_list.append(class_dict)

    session.close()

    if to_csv:
        csv_data = StringIO()
        csv_columns = list(class_list[0].keys())
        writer = csv.DictWriter(csv_data, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(class_list)
        output = make_response(csv_data.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"

        return output

    return jsonify(class_list)


@app.route("/")
def schedule():
    classes = get("http://127.0.0.1:5000/classes/0/0/0/0")
    return render_template("schedule.html", classes=classes.json(), title='Расписание',
                           is_operator=current_user.is_authenticated and current_user.role_id == 1)


@app.route('/add_class', methods=['POST'])
@operator_required
def add_class():
    class_data = {
        'start': request.form['start'],
        'end': request.form['end'],
        'class_number': request.form['class_number'],
        'weekday': request.form['weekday'],
        'week_parity': request.form['week_parity'],
        'subject_id': request.form['subject'],
        'professor_id': request.form['professor'],
        'classroom_id': request.form['classroom'],
        'group_id': request.form['group']
    }

    new_class = data.classes.Class(
        start=class_data['start'],
        end=class_data['end'],
        class_number=class_data['class_number'],
        weekday=class_data['weekday'],
        week_parity=class_data['week_parity'],
        subject_id=class_data['subject_id'],
        professor_id=class_data['professor_id'],
        classroom_id=class_data['classroom_id'],
        group_id=class_data['group_id']
    )

    session = db_session.create_session()

    try:
        session.add(new_class)
        session.commit()
        session.close()
        return jsonify({'message': 'Class added successfully'}), 201
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({'message': f'Failed to add class. Error: {str(e)}'}), 500


@app.route('/add_class', methods=['GET'])
@operator_required
def show_add_class_form():
    session = db_session.create_session()
    session.close()
    return render_template('add_class.html',
                           title='Добавление записи',
                           professors=session.query(data.professors.Professor),
                           groups=session.query(data.groups.Group),
                           classrooms=session.query(data.classrooms.Classroom),
                           subjects=session.query(data.subjects.Subject))


@app.route('/delete_class/<int:class_id>', methods=['POST'])
@operator_required
def delete_class(class_id):
    session = db_session.create_session()
    try:
        class_to_delete = session.query(data.classes.Class).filter_by(id=class_id).first()

        if class_to_delete:
            session.delete(class_to_delete)
            session.commit()
            session.close()
            return jsonify({'message': f'Class with id {class_id} deleted successfully'}), 200
        else:
            session.close()
            return jsonify({'message': f'Class with id {class_id} not found'}), 404

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({'message': f'Failed to delete class. Error: {str(e)}'}), 500


def backup_database():
    PG_DUMP_PATH = "C:\\Program Files\\PostgreSQL\\12\\bin\\pg_dump.exe"
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file = f"'{db_config['db_name']}_backup_{timestamp}.sql'"

    dump_command = [
        PG_DUMP_PATH,
        '-U', db_config['user_name'],
        '-h', db_config['host'],
        '-p', db_config['port'],
        '-d', db_config['db_name'],
        '-f', backup_file
    ]
    os.environ['PGPASSWORD'] = db_config['password']

    try:
        subprocess.run(dump_command, check=True)
        print(f'Backup created successfully: {backup_file}')
    except BaseException as e:
        print(f'Backup failed: {e}')

    try:
        y = yadisk.YaDisk(token='y0_AgAAAAAsjp9kAAsQAAAAAAD2OW10Jk4gDd_aQIejb5mEBaDjpOp_IAg')
        y.upload(backup_file, f"Backups/{backup_file}")
    except BaseException as e:
        print(f'Backup failed: {e}')


db_config = {
    'server_name': 'postgres',
    'user_name': 'postgres',
    'password': '12345678',
    'db_name': 'schedule',
    'host': 'localhost',
    'port': '5432'
}

scheduler = BackgroundScheduler()
scheduler.add_job(backup_database, 'cron', hour=0)


def main():
    db_session.global_init(db_config['server_name'], db_config['password'], db_config['db_name'])
    app.run()


scheduler = BackgroundScheduler()
scheduler.add_job(backup_database, 'cron', hour=0)
if __name__ == '__main__':
    scheduler.start()
    main()
