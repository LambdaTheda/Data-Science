from os import getenv
from flask import Flask, request, render_template
from dotenv import load_dotenv
from .model import db

# load_dotenv

def create_app():
'''Create and configure an instance of the Flask application'''

    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = getenv('DATABASE_URL')  # <---- work on getting the URL corrected
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

   # Load the files from .env file:
    load_dotenv()

    # Configuring DB:
    app.config['DEBUG'] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")

    # Establish the connection and cursor objects and display them:
    connection = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)
    print("Connection: ", connection)
    cursor = connection.cursor()
    print("Cursor: ", type(cursor))

    # Binding the instance to the flask app and initialize:
    db = SQLAlchemy(app)
    db.init_app(app)

    @app.route('/')
    def root():
        return 'PLACE HOLDER FOR FLASK APP!!

    return app