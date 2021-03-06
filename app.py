import os

from flask import Flask
from flask_restful import Api

from api import *

app = Flask(__name__)
api = Api(app)
api.add_resource(CollaborativeFilteringAPI, "/api/recommender/collaborativefiltering")
api.add_resource(ContentBasedFilteringAPI, "/api/recommender/contentbasedfiltering")
api.add_resource(ArticleApi, "/api/article/details")
api.add_resource(ArticleByAuthorIdApi, "/api/article/articleByAuthorId")
api.add_resource(AuthorListApi, "/api/author/authorlist")
api.add_resource(AuthorDetailsApi, "/api/author/authorDetails")
api.add_resource(ArticleListApi, "/api/article/articleList")
api.add_resource(ArticleByIdApi, "/api/article/articleById")
api.add_resource(AuthorUnsubscribeApi, "/api/author/unsubscribe")
api.add_resource(AuthorUnsubscribeReasonApi, "/api/author/unsubscribeReason")
api.add_resource(AuthorUnsubscribeListApi, "/api/author/unsubscribeList")

api.add_resource(AddQueue, "/api/email/addQueue")
api.add_resource(QueueList, "/api/email/queueList")
api.add_resource(MailDetails, "/api/email/mailDetails")
api.add_resource(HistoryList, "/api/email/historyList")
api.add_resource(UpdateSentStatus, "/api/email/updateSentStatus")
api.add_resource(CheckQueue, "/api/email/checkQueue")


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    #port = int(os.environ.get('PORT', 5000))
    app.run(debug = True)
    #app.run(debug = False)