from flask import Flask
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'


def main():
    db_session.global_init("postgres", "12345678", "schedule")
    app.run()


if __name__ == '__main__':
    main()
