import functools
import json
import time

from flask_restful import Resource, reqparse, abort
from py2neo import Graph

api_put_args = reqparse.RequestParser()

api_put_args.add_argument("api-key", type=str, help="api-key is required.", required=True)
api_put_args.add_argument("title", type=str, help="title is required.", required=True)
api_put_args.add_argument("receiverId", type=str, help="receiverId is required.", required=False)
api_put_args.add_argument("articleId", type=str, help="articleId is required.", required=False)
api_put_args.add_argument("senderName", type=str, help="senderName is required.", required=False)
api_put_args.add_argument("senderMail", type=str, help="senderMail is required.", required=False)

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

class AddQueue(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title       = api_args["title"]
        receiverId    = api_args["receiverId"]
        articleId   = api_args["articleId"]
        senderName  = api_args["senderName"]
        senderMail  = api_args["senderMail"]
        curTime = time.time()

        query = """
        MATCH (a:Author {authorId: $receiverId})
        MATCH (source:Article {eid: $articleId})
        MERGE (source)-[m:MAIL_TO]->(a)
        SET m.senderName = $senderName,
        m.senderMail = $senderMail,
        m.mailContent = $title,
        m.status = "queue",
        m.addedDatetime = $curTime,
        m.mailedDatetime = ""
        RETURN a
        """

        result = graph.run(query, dict(title = title, receiverId = receiverId, articleId = articleId, senderName = senderName, senderMail = senderMail, curTime = curTime))
        result = result.data()
        return result

class QueueList(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]

        query = """
        MATCH (source:Article)-[m:MAIL_TO]->(a:Author)
        WHERE m.status = "queue"
        RETURN a,m,source
        """

        result = graph.run(query, dict(title = title))
        result = result.data()
        return result

class MailList(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]

        query = """
        MATCH (a:Author)
        WHERE  a.authorId = $title
        RETURN a
        """

        result = graph.run(query, dict(title = title))
        result = result.data()
        return result

class MailDetails(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]
        receiverId    = api_args["receiverId"]
        articleId   = api_args["articleId"]

        query = """
        MATCH (source:Article {eid: $articleId})-[m:MAIL_TO]->(a:Author {authorId: $receiverId})
        RETURN a,m,source
        """

        result = graph.run(query, dict(title = title, receiverId = receiverId, articleId = articleId))
        result = result.data()
        return result

class HistoryList(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]

        query = """
        MATCH (source:Article)-[m:MAIL_TO]->(a:Author)
        WHERE m.status = "sent"
        RETURN a,m,source
        """

        result = graph.run(query, dict(title = title))
        result = result.data()
        return result

