import os

from flask import Flask
from flask_restful import Api

from api import RecommenderApi

app = Flask(__name__)
api = Api(app)
api.add_resource(RecommenderApi, "/api/recommender")

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    #port = int(os.environ.get('PORT', 5000))
    app.run(debug = True)
    #app.run(debug = False)