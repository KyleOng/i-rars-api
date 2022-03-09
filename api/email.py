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
api_put_args.add_argument("senderUserId", type=str, help="senderUserId is required.", required=False)
api_put_args.add_argument("sentType", type=str, help="sentType is required.", required=False)
api_put_args.add_argument("status", type=str, help="status is required.", required=False)
api_put_args.add_argument("mailId", type=str, help="mailId is required.", required=False)
api_put_args.add_argument("mailContentTop", type=str, help="mailContentTop is required.", required=False)
api_put_args.add_argument("mailContentBottom", type=str, help="mailContentBottom is required.", required=False)
api_put_args.add_argument("mailSubject", type=str, help="mailSubject is required.", required=False)

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
        title               = api_args["title"]
        receiverId          = api_args["receiverId"]
        articleId           = api_args["articleId"]
        senderName          = api_args["senderName"]
        senderMail          = api_args["senderMail"]
        senderUserId        = api_args["senderUserId"]
        mailId              = api_args["mailId"]
        mailContentTop      = api_args["mailContentTop"]
        mailContentBottom   = api_args["mailContentBottom"]
        mailSubject         = api_args["mailSubject"]

        curTime = time.time()

        query = """
        MATCH (a:Author {authorId: $receiverId})
        MATCH (source:Article {eid: $articleId})
        MERGE (u:MmuUser {userId: $senderUserId})
        ON CREATE
            SET u.createdDatetime = $curTime
        MERGE (mail:Mail {mailId: $mailId})
        ON CREATE
            SET mail.senderName = $senderName,
            mail.senderMail = $senderMail,
            mail.mailContentTop = $mailContentTop,
            mail.mailContentBottom = $mailContentBottom,
            mail.mailSubject = $mailSubject,
            mail.status = "queue",
            mail.addedDatetime = $curTime,
            mail.mailedDatetime = ""
        ON MATCH
            SET mail.updateDatetime = $curTime,
            mail.mailContentTop = $mailContentTop,
            mail.mailSubject = $mailSubject,
            mail.mailContentBottom = $mailContentBottom
        MERGE (mail)-[:INCLUDE]->(source)
        MERGE (u)-[:GENERATE]->(mail)-[:MAIL_TO]->(a)
        
        RETURN mail
        """
      
        result = graph.run(query, dict(title = title, mailId = mailId, mailSubject = mailSubject, mailContentTop = mailContentTop, mailContentBottom = mailContentBottom, receiverId = receiverId, articleId = articleId, senderName = senderName, senderMail = senderMail, curTime = curTime, senderUserId = senderUserId))
        result = result.data()
        return result

class QueueList(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args    = api_put_args.parse_args()
        title       = api_args["title"]
        senderUserId    = api_args["senderUserId"]

        today   = date.today()
        d1      = today.strftime("%Y-%m-%d")

        fromDate    = ( api_args["fromDate"] or d1 )
        toDate      = ( api_args["toDate"] or d1 )

        ts1 = ciso8601.parse_datetime(fromDate+" 00:00:00")
        ts2 = ciso8601.parse_datetime(toDate+" 23:59:59")

        fromDate    = time.mktime(ts1.timetuple())
        toDate      = time.mktime(ts2.timetuple()) 
        
        if senderUserId == 'admin':
            query = """
            MATCH (source:Article)<-[:INCLUDE]-(m:Mail)-[:MAIL_TO]->(a:Author)
            MATCH (u:MmuUser)-[:GENERATE]->(m)
            WHERE m.status = "queue" AND  m.addedDatetime >= $fromDate AND m.addedDatetime <= $toDate
            RETURN a{.preferredName_full, .authorId, .emailAddress},m{.addedDatetime, .senderName, .updateDatetime, .mailedDatetime, .mailId, .senderMail, .status},COLLECT(source{.title, .eid}) as source,u
            """
        else:
            query = """
            MATCH (source:Article)<-[:INCLUDE]-(m:Mail)-[:MAIL_TO]->(a:Author)
            MATCH (u:MmuUser)-[:GENERATE]->(m)
            WHERE m.status = "queue" 
            AND  m.addedDatetime >= $fromDate AND m.addedDatetime <= $toDate 
            AND u.userId = $senderUserId
            RETURN a{.preferredName_full, .authorId, .emailAddress},m{.addedDatetime, .senderName, .updateDatetime, .mailedDatetime, .mailId, .senderMail, .status},COLLECT(source{.title, .eid}) as source,u
            """

        result = graph.run(query, dict(title = title, fromDate = fromDate, toDate = toDate, senderUserId = senderUserId))
        result = result.data()
        return result

class MailDetails(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]
        mailId   = api_args["mailId"]

        query = """
        MATCH (source:Article)<-[:INCLUDE]-(m:Mail{mailId: $mailId})
        MATCH (u:MmuUser)-[:GENERATE]->(m)
        MATCH (m)-[:MAIL_TO]->(a:Author)
        WITH source, m, u, a
        OPTIONAL MATCH (source)<-[:WRITE]-(writer:Author)
        WITH source, m, u, a, COLLECT(writer.preferredName_full) as author
        WITH  (a{.preferredName_full, .authorId, .emailAddress}) as a,m,COLLECT(source) as sources,u, COLLECT(author) as author
        MATCH (source:Article)<-[:INCLUDE]-(:Mail{mailId: $mailId})
        WITH  a,m,sources,u,author, source
        OPTIONAL MATCH(source)-[:CONTAIN]->(k:Keyword)
        WITH a,m,sources,u,author,  collect(k.keyword) as keywords , source{.eid} as source
        RETURN a,m,sources as source,u,author,  collect(keywords) as keywords 

        """

        result = graph.run(query, dict(title = title, mailId = mailId))
        result = result.data()
        return result

class HistoryList(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]
        senderUserId    = api_args["senderUserId"]
        
        today   = date.today()
        d1      = today.strftime("%Y-%m-%d")

        fromDate    = ( api_args["fromDate"] or d1 )
        toDate      = ( api_args["toDate"] or d1 )

        ts1 = ciso8601.parse_datetime(fromDate+" 00:00:00")
        ts2 = ciso8601.parse_datetime(toDate+" 23:59:59")

        fromDate    = time.mktime(ts1.timetuple())
        toDate      = time.mktime(ts2.timetuple()) 

        if senderUserId == 'admin':
            query = """
            MATCH (source:Article)<-[:INCLUDE]-(m:Mail)-[:MAIL_TO]->(a:Author)
            MATCH (u:MmuUser)-[:GENERATE]->(m)
            WHERE m.status = "sent" AND  m.mailedDatetime >= $fromDate AND m.mailedDatetime <= $toDate 
            RETURN a{.preferredName_full, .authorId, .emailAddress},m{.addedDatetime, .senderName, .updateDatetime, .mailedDatetime, .mailId, .senderMail, .status, .sentType},COLLECT(source{.title, .eid}) as source,u
            """
        else:
            query = """
            MATCH (source:Article)<-[:INCLUDE]-(m:Mail)-[:MAIL_TO]->(a:Author)
            MATCH (u:MmuUser)-[:GENERATE]->(m)
            WHERE m.status = "sent" AND  m.mailedDatetime >= $fromDate AND m.mailedDatetime <= $toDate AND m.senderUserId = $senderUserId
            AND u.userId = $senderUserId
            RETURN a{.preferredName_full, .authorId, .emailAddress},m{.addedDatetime, .senderName, .updateDatetime, .mailedDatetime, .mailId, .senderMail, .status, .sentType},COLLECT(source{.title, .eid}) as source,u
            """
        result = graph.run(query, dict(title = title, fromDate = fromDate, toDate = toDate, senderUserId = senderUserId))
        result = result.data()
        return result

class UpdateSentStatus(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args        = api_put_args.parse_args()
        title           = api_args["title"]
        receiverId      = api_args["receiverId"]
        articleId       = api_args["articleId"]
        mailId          = api_args["mailId"]
        sentType        = api_args["sentType"]
        status          = api_args["status"]

        curTime         = time.time()

        query = """
        MATCH (m:Mail {mailId: $mailId})
        SET m.status = $status, 
        m.mailedDatetime = $curTime, 
        m.sentType = $sentType
        RETURN m
        """

        result = graph.run(query, dict(status = status,title = title, mailId = mailId, curTime = curTime, sentType = sentType))
        result = result.data()
        return result

class CheckQueue(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title               = api_args["title"]
        receiverId          = api_args["receiverId"]
        senderUserId        = api_args["senderUserId"]

        query = """
        MATCH (u:MmuUser {userId: $senderUserId})-[:GENERATE]->(mail)-[:MAIL_TO]->(a:Author {authorId: $receiverId})
        WHERE mail.status="queue"
        RETURN mail
        """
      
        result = graph.run(query, dict(receiverId = receiverId, senderUserId = senderUserId))
        result = result.data()
        return result