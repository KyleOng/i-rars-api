import functools
import json
import os

from flask_restful import Resource, reqparse, abort
from py2neo import Graph

api_put_args = reqparse.RequestParser()

api_put_args.add_argument("api-key", type=str, help="api-key is required.", required=True)
api_put_args.add_argument("title", type=str, help="title is required.", required=True)

#get from env (wsgi ini)
api_key     = os.environ.get('API_KEY', '')
url         = os.environ.get('URL', '')
username    = os.environ.get('USERNAME', '')
password    = os.environ.get('PASSWORD', '')

# if env not loaded
if url == '':
    with open("config.json") as f:
        try:
            data        = json.load(f)
            api_key     = data["api-key"]
            url         = data["url"]
            username    = data["username"]
            password    = data["password"]

        except Exception as e:
            pass
            raise e
            
graph = Graph(url, auth=(username, password))   

def authentication(func):
    # Future use: Authentication api key from database

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if api_put_args.parse_args()["api-key"] != api_key:
            abort(404, message = "Api-key is invalid.") 
        return func(*args, **kwargs)
    return wrapper

class CollaborativeFilteringAPI(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]

        query = """
        MATCH (source:Article {eid: $title})
        <-[:CITE]-(source_cite_bys:Article)
        -[:CITE]->(target:Article)
        <-[:CITE]-(target_cite_bys:Article)
        <-[:WRITE]-(a:Author)
        WHERE source <> target
        AND source_cite_bys <> target_cite_bys 
        AND ( a.mailSubscribeStatus = "subscribe" OR a.mailSubscribeStatus IS NULL)
        AND a.emailAddress IS NOT NULL
        AND NOT (a)-[:WRITE]->(source) 
        WITH a, source, count(a) as frequency
        OPTIONAL MATCH (source)<-[:INCLUDE]-(m:Mail)-[:MAIL_TO]->(a)
        WHERE m.status <> "canceled"
        RETURN a {.preferredName_full, .emailAddress, .latestAffiliatedInstitution_name, .authorId}, m, frequency
        ORDER BY frequency DESC LIMIT 300
        """

        result = graph.run(query, dict(title = title))
        result = result.data()
        return result

class ContentBasedFilteringAPI(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]

        query = """
        MATCH (source:Article {eid: $title})
        -[:CONTAIN]->(:Keyword)
        <-[:CONTAIN]-(target:Article)
        <-[:WRITE]-(a:Author)
        WHERE source <> target
        AND NOT (a)-[:WRITE]->(source)
        AND ( a.mailSubscribeStatus = "subscribe" OR a.mailSubscribeStatus IS NULL)
        AND a.emailAddress IS NOT NULL
        WITH a, source, count(a) as frequency
        OPTIONAL MATCH (source)<-[:INCLUDE]-(m:Mail)-[:MAIL_TO]->(a)
        WHERE m.status <> "canceled"
        RETURN a {.preferredName_full, .emailAddress, .latestAffiliatedInstitution_name, .authorId}, m, frequency
        ORDER BY frequency DESC LIMIT 300
        """

        result = graph.run(query, dict(title = title))
        result = result.data()
        return result

