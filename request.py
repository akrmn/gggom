class Request:

    def __init__(self, movie, server, client):
        self.movie = movie
        self.server = server
        self.client = client

    def __str__(self):
        return('request: movie: ' + str(self.movie) + ', server: ' +
               str(self.server) + ', client: ' + str(self.client))

    def to_row(self):
        return [self.movie.id_movie, self.client.username]


class RequestList:
    """ Tiene una lista de requests """
    def __init__(self):
        self.requests = []

    def is_element(self, request):
        return request in self.requests

    def is_empty(self):
        return not bool(self.requests)

    def add_request(self, request):
        self.requests.append(request)

    def get_request(self, request):
        for r in self.requests:
            if r == request:
                return r
        return None

    def get_requests_from_server(self, server):
        reqs = []
        for r in self.requests:
            if server == r.server:
                reqs.append(r)
        return reqs

    def print_requests(self):
        for request in self.requests:
            print(str(request))
