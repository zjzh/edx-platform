from datetime import datetime
from cProfile import Profile
from pstats import Stats

class ProfilingMiddleware(object):

    def __init__(self):
        self.prof = None

    def process_request(self, request):
        if request.GET.get('profile_name'):
            self.prof = Profile()
            self.prof.enable()

    def process_response(self, request, response):
        if self.prof:
            self.prof.disable()
            s = Stats(self.prof)
            s.dump_stats(request.GET['profile_name'])

        self.prof = None
        return response