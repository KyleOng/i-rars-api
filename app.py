import os

from flask import Flask
from flask_restful import Api

from api import *

app = Flask(__name__)
api = Api(app)
api.add_resource(CollaborativeFilteringAPI, "/api/recommender/collaborativefiltering")
api.add_resource(ContentBasedFilteringAPI, "/api/recommender/contentbasedfiltering")
api.add_resource(ArticleApi, "/api/article/details")
api.add_resource(ArticleAuthorApi, "/api/article/author")
api.add_resource(ArticleByAuthorApi, "/api/article/articleByAuthor")

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    #port = int(os.environ.get('PORT', 5000))
    app.run(debug = True)
    #app.run(debug = False)