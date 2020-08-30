from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import flask_cors
from flask_cors import CORS
from medcab.models import DB, Strain
import os
from os import getenv
import psycopg2
import pickle
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from spacy.lang.en import English
from spacy.tokenizer import Tokenizer


# changed from relative to to full path
strains = pd.read_csv("https://raw.githubusercontent.com/Build-Week-Med-Cabinet-3/Data-Science/master/API/nn_model_strains.csv")

nlp=English()
tokenizer = Tokenizer(nlp.vocab)
tf = TfidfVectorizer(stop_words="english")
transformer = TfidfVectorizer(stop_words="english", min_df=0.025, max_df=0.98, ngram_range=(1,3))


dtm = transformer.fit_transform(strains['lemmas'])
dtm = pd.DataFrame(dtm.todense(), columns=transformer.get_feature_names())

model = NearestNeighbors(n_neighbors=10, algorithm='kd_tree')
model.fit(dtm)

def predict(request_text):
    '''Prediction for user'''
    transformed = transformer.transform([request_text])
    dense = transformed.todense()
    recommendations = model.kneighbors(dense)[1][0]
    output_array = []
    for recommendation in recommendations:
        strain = strains.iloc[recommendation]
        output = strain.drop(['Unnamed: 0', 'name', 'ailment', 'all_text', 'lemmas']).to_dict()
        output_array.append(output)
        print('output_array')
    return output_array

def create_app():
    '''Create and configure an instance of the Flask application'''
    app = Flask(__name__)
    CORS(app)
    
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

    # Route for root: (Home Page)
    @app.route('/')
    def root():
        """Landing page for medcab"""
        DB.create_all()
        return 'WELCOME TO OUR MEDICINE CABINET!!'

    # Route for predictions: (previously endpoint was named '/test')
    @app.route('/predict_strain', methods=['POST', 'GET'])
    def predict_strain():
        """Page that will load the user's recommendation"""
        data = request.get_json(force=True)  # parse the obj, then extract what we want
        predictions = predict(data['input']) # pass in user's input to the ML pred model
        return jsonify(predictions)

    return app