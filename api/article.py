import functools
import json

from flask_restful import Resource, reqparse, abort
from py2neo import Graph

api_put_args = reqparse.RequestParser()

api_put_args.add_argument("api-key", type=str, help="api-key is required.", required=True)
api_put_args.add_argument("title", type=str, help="title is required.", required=True)

with open("config.json") as f:
    try:
        data = json.load(f)
        api_key = data["api-key"]
        url = data["url"]
        username = data["username"]
        password = data["password"]
        graph = Graph(url, auth=(username, password))    

        graph.run("Match () Return 1 Limit $one", {"one": 1})
    except Exception as e:
        pass
        raise e

def authentication(func):
    # Future use: Authentication api key from database

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if api_put_args.parse_args()["api-key"] != api_key:
            abort(404, message = "Api-key is invalid.") 
        return func(*args, **kwargs)
    return wrapper

class ArticleApi(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]

        query = """
        MATCH (source:Article)
        <-[:WRITE]-(a:Author)
        WHERE toLower(source.title) CONTAINS toLower($title)
        WITH source, collect(a) as author
        OPTIONAL MATCH(source)-[:CONTAIN]->(k:Keyword)
        RETURN author, source, collect(k.keyword) as keywords
        """

        result = graph.run(query, dict(title = title))
        result = result.data()
        return result

class ArticleByAuthorApi(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]

        query = """
        MATCH (source:Article )
        <-[:WRITE]-(a:Author)
        WHERE  toLower(a.`preferredName_last`) =  toLower($title) OR  toLower(a.`preferredName_first`) =  toLower($title)
        WITH source
        MATCH (source)<-[:WRITE]-(authors:Author)
        RETURN source, collect(authors) as authors
        """

        result = graph.run(query, dict(title = title))
        result = result.data()
        return result

class ArticleAuthorApi(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]

        query = """
        MATCH (source:Article {title: $title})
        <-[:WRITE]-(a:Author)
        RETURN a
        """

        result = graph.run(query, dict(title = title))
        result = result.data()
        return result
