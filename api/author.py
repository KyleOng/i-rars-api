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

class AuthorListApi(Resource):
    @authentication
    def post(self, *args, **kwargs):
        api_args = api_put_args.parse_args()
        title = api_args["title"]

        titleNoSpace = title.replace(" ", "")
        titleNoDash = title.replace("-", "")
        titleDashToSpace = title.replace("-", " ")

        titleSplitArray = title.split(" ")
        titleSplit = titleSplitArray[0]
        titleSplit = titleSplit.replace("-", "")
        titleSplitDashToSpace = titleSplit.replace("-", " ")

        # if len(titleSplitArray) > 1:
        #     titleSplit2 = titleSplitArray[1]
        #     titleSplit2 = titleSplit2.replace("-", "")
        #     titleSplitDashToSpace2 = titleSplit2.replace("-", " ")
        # else :
        #     titleSplit2 = titleSplit
        #     titleSplitDashToSpace2 = titleSplitDashToSpace

        query = """
        MATCH (a:Author)
        WHERE  (toLower(a.`preferredName_last`) CONTAINS  toLower($title) OR  toLower(a.`preferredName_first`) =  toLower($title))
        OR (toLower(a.`preferredName_last`) CONTAINS  toLower($titleNoSpace) OR  toLower(a.`preferredName_first`) =  toLower($titleNoSpace))
        OR (toLower(a.`preferredName_last`) CONTAINS  toLower($titleNoDash) OR  toLower(a.`preferredName_first`) =  toLower($titleNoDash))
        OR (toLower(a.`preferredName_last`) CONTAINS  toLower($titleSplit) OR  toLower(a.`preferredName_first`) =  toLower($titleSplit))
        OR (toLower(a.`preferredName_last`) CONTAINS  toLower($titleDashToSpace) OR  toLower(a.`preferredName_first`) =  toLower($titleDashToSpace))
        OR (toLower(a.`preferredName_last`) CONTAINS  toLower($titleSplitDashToSpace) OR  toLower(a.`preferredName_first`) =  toLower($titleSplitDashToSpace))
        
        RETURN a
        """

        result = graph.run(query, dict(title = title, titleNoSpace = titleNoSpace, titleNoDash = titleNoDash,titleDashToSpace = titleDashToSpace, titleSplit = titleSplit, titleSplitDashToSpace = titleSplitDashToSpace))
        # result = graph.run(query, dict(title = title, titleNoSpace = titleNoSpace, titleNoDash = titleNoDash,titleDashToSpace = titleDashToSpace, titleSplit = titleSplit, titleSplitDashToSpace = titleSplitDashToSpace , titleSplit2 = titleSplit2, titleSplitDashToSpace2 = titleSplitDashToSpace2))
        result = result.data()
        return result

class AuthorDetailsApi(Resource):
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


