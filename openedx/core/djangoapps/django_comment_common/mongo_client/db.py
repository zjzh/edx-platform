from .mongo_connection import MongoConnection


class DiscussionStore:
    """Discussion Store"""

    def __init__(self):
        doc_store_config = {
            'db': 'cs_comments_service',
            'authsource': '',
            'connectTimeoutMS': 2000,
            'host': ['edx.devstack.mongo'],
            'password': 'password',
            'port': 27017,
            'read_preference': 'PRIMARY',
            'replicaSet': '',
            'socketTimeoutMS': 3000,
            'ssl': False,
            'user': 'cs_comments_service'
        }
        self.db_connection = MongoConnection(**doc_store_config)
        self.filter_options = ['unread', 'unanswered', 'flagged']

    def _get_filter_option(self, query_params):
        filter_by = ''
        for option in self.filter_options:
            if query_params.get(option) :
                filter_by = option
                break
        return filter_by

    def close_connections(self):
        """
        Closes any open connections to the underlying databases
        """
        pass

    def find_course_threads(self, query_params):
        query_params['filter_by'] = self._get_filter_option(query_params)

        course_threads = self.db_connection.get_content_by_course(query_params)
        return course_threads

    def get_user(self, user_id):
        return self.db_connection.get_user_details(user_id)

    def get_user_read_states(self, user_id, course_id):
        self.db_connection.get_user_read_state_for_course(user_id, course_id)
