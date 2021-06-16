from xmodule.mongo_utils import connect_to_mongodb, create_collection_index
from bson.objectid import ObjectId


class MongoConnection:
    """
    Segregation of pymongo functions from the data modeling mechanisms for split modulestore.
    """

    def __init__(
        self, db, host, port=27017, tz_aware=True, user=None, password=None,
        asset_collection=None, retry_wait_time=0.1, **kwargs  # lint-amnesty, pylint: disable=unused-argument
    ):
        """
        Create & open the connection, authenticate, and provide pointers to the collections
        """
        # Set a write concern of 1, which makes writes complete successfully to the primary
        # only before returning. Also makes pymongo report write errors.
        kwargs['w'] = 1

        self.database = connect_to_mongodb(
            db, host,
            port=port, tz_aware=tz_aware, user=user, password=password,
            retry_wait_time=retry_wait_time, **kwargs
        )

        self.contents = self.database['contents']
        self.subscriptions = self.database['subscriptions']
        self.users = self.database['users']

    def get_content_by_course(self, query_params):
        """"""
        query = {
            'thread_type': {'$in': ['discussion', 'question']},
            'course_id': query_params['course_id']
        }
        breakpoint()
        filter_by = query_params['filter_by']
        if filter_by == 'unread':
            read_states = self.get_user_read_state_for_course(query_params['user_id'], query_params['course_id'])
            query['_id'] = {'$nin': [ObjectId(_id) for _id in read_states]}
        if filter_by == 'unanswered':
            answered_threads = self.get_answerd_course_threads(query_params["course_id"])
            query['_id'] = {'$nin': answered_threads}
        docs = [doc for doc in self.contents.find(query)]
        return docs

    def get_user_details(self, user_id):
        return self.users.find_one({'external_id': f'{user_id}'})

    def get_user_read_state_for_course(self, user_id, course_id):
        query = {'external_id': f'{user_id}', 'read_states.course_id': course_id}
        user_read_states = self.users.find_one(query, {"read_states.$": 1})
        if not user_read_states:
            return []
        return list(user_read_states['read_states'][0]['last_read_times'].keys())

    def get_answerd_course_threads(self, course_id):
        answered_threads = []
        docs = self.contents.find({
            'course_id': course_id,
            'parent_id': {'$exists': 0},
            "comment_thread_id": {"$exists": 1},
        }, {
            "_id": 0,
            "comment_thread_id": 1
        })
        if not docs:
            return []

        for doc in docs:
            answered_threads.append(doc['comment_thread_id'])
        return answered_threads
