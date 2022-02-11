import functools
import json
import os
import time
import ciso8601
from datetime import date

from flask_restful import Resource, reqparse, abort
from py2neo import Graph

api_put_args = reqparse.RequestParser()

api_put_args.add_argument("api-key", type=str, help="api-key is required.", required=True)
api_put_args.add_argument("title", type=str, help="title is required.", required=True)
api_put_args.add_argument("receiverId", type=str, help="receiverId is required.", required=False)
api_put_args.add_argument("articleId", type=str, help="articleId is required.", required=False)
api_put_args.add_argument("senderName", type=str, help="senderName is required.", required=False)
api_put_args.add_argument("senderMail", type=str, help="senderMail is required.", required=False)
api_put_args.add_argument("fromDate", type=str, help="fromDate is required.", required=False)
api_put_args.add_argument("toDate", type=str, help="toDate is required.", required=False)

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
        api_args    = api_put_args.parse_args()
        title       = api_args["title"]

        today   = date.today()
        d1      = today.strftime("%Y-%m-%d")

        fromDate    = ( api_args["fromDate"] or d1 )
        toDate      = ( api_args["toDate"] or d1 )

        ts1 = ciso8601.parse_datetime(fromDate+" 00:00:00")
        ts2 = ciso8601.parse_datetime(toDate+" 23:59:59")

        fromDate    = time.mktime(ts1.timetuple())
        toDate      = time.mktime(ts2.timetuple()) 
        
        query = """
        MATCH (source:Article)-[m:MAIL_TO]->(a:Author)
        WHERE m.status = "queue" AND  m.addedDatetime >= $fromDate AND m.addedDatetime <= $toDate
        RETURN a,m,source
        """

        result = graph.run(query, dict(title = title, fromDate = fromDate, toDate = toDate))
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
        
        today   = date.today()
        d1      = today.strftime("%Y-%m-%d")

        fromDate    = ( api_args["fromDate"] or d1 )
        toDate      = ( api_args["toDate"] or d1 )

        ts1 = ciso8601.parse_datetime(fromDate+" 00:00:00")
        ts2 = ciso8601.parse_datetime(toDate+" 23:59:59")

        fromDate    = time.mktime(ts1.timetuple())
        toDate      = time.mktime(ts2.timetuple()) 

        query = """
        MATCH (source:Article)-[m:MAIL_TO]->(a:Author)
        WHERE m.status = "sent" AND  m.mailedDatetime >= $fromDate AND m.mailedDatetime <= $toDate 
        RETURN a,m,source
        """

        result = graph.run(query, dict(title = title, fromDate = fromDate, toDate = toDate))
        result = result.data()
        return result

class UpdateSentStatus(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args        = api_put_args.parse_args()
        title           = api_args["title"]
        receiverId      = api_args["receiverId"]
        articleId       = api_args["articleId"]
        curTime         = time.time()

        query = """
        MATCH (source:Article {eid: $articleId})-[m:MAIL_TO]->(a:Author {authorId: $receiverId})
        SET m.status = "sent", 
        m.mailedDatetime = $curTime
        RETURN m
        """

        result = graph.run(query, dict(title = title, receiverId = receiverId, articleId = articleId, curTime = curTime))
        result = result.data()
        return result