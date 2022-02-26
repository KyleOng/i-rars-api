import functools
import json
import os

from flask_restful import Resource, reqparse, abort
from py2neo import Graph

api_put_args = reqparse.RequestParser()

api_put_args.add_argument("api-key", type=str, help="api-key is required.", required=True)
api_put_args.add_argument("title", type=str, help="title is required.", required=True)
api_put_args.add_argument("firstname", type=str, help="firstname is required.", required=False)
api_put_args.add_argument("lastname", type=str, help="lastname is required.", required=False)

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

        firstname = api_args["firstname"]
        lastname = api_args["lastname"]

        firstnameNoSpace = firstname.replace(" ", "")
        firstnameNoDash = firstname.replace("-", "")
        firstnameDashToSpace = firstname.replace("-", " ")

        lastnameNoSpace = lastname.replace(" ", "")
        lastnameNoDash = lastname.replace("-", "")
        lastnameDashToSpace = lastname.replace("-", " ")

        if firstname == '':
            query = """
            MATCH (a:Author)
            WHERE  (toLower(a.`preferredName_last`) CONTAINS  toLower($lastname) )
            OR (toLower(a.`preferredName_last`) CONTAINS  toLower($lastnameNoSpace) )
            OR (toLower(a.`preferredName_last`) CONTAINS  toLower($lastnameNoDash) )
            OR (toLower(a.`preferredName_last`) CONTAINS  toLower($lastnameDashToSpace) )
        
            RETURN a
            """
        elif lastname == '':
            query = """
            MATCH (a:Author)
            WHERE  ( toLower(a.`preferredName_first`) =  toLower($firstname))
            OR ( toLower(a.`preferredName_first`) =  toLower($firstnameNoSpace))
            OR ( toLower(a.`preferredName_first`) =  toLower($firstnameNoDash))
            OR ( toLower(a.`preferredName_first`) =  toLower($firstnameDashToSpace))
        
            RETURN a
            """
        else:
            query = """
            MATCH (a:Author)
            WHERE  (toLower(a.`preferredName_last`) CONTAINS  toLower($lastname) OR  toLower(a.`preferredName_first`) =  toLower($firstname))
            OR (toLower(a.`preferredName_last`) CONTAINS  toLower($lastnameNoSpace) OR  toLower(a.`preferredName_first`) =  toLower($firstnameNoSpace))
            OR (toLower(a.`preferredName_last`) CONTAINS  toLower($lastnameNoDash) OR  toLower(a.`preferredName_first`) =  toLower($firstnameNoDash))
            OR (toLower(a.`preferredName_last`) CONTAINS  toLower($lastnameDashToSpace) OR  toLower(a.`preferredName_first`) =  toLower($firstnameDashToSpace))
        
            RETURN a
            """

        result = graph.run(query, dict(firstname = firstname, firstnameNoSpace = firstnameNoSpace, firstnameNoDash = firstnameNoDash,firstnameDashToSpace = firstnameDashToSpace, lastname = lastname, lastnameNoSpace = lastnameNoSpace, lastnameNoDash = lastnameNoDash, lastnameDashToSpace = lastnameDashToSpace))
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


