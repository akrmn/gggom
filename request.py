class Request:

    def __init__(self, movie, server):
        self.movie = movie
        self.server = server

    def __str__(self):
        return('request: movie:' + str(self.movie) + ', server:' +
               str(self.server))


# class RequestList:
#     """ Tiene una lista de requests """
#     def __init__(self):
#         self.requests = []
#
#     def is_element(self, request):
#         return request in self.requests
#
#     def add_request(self, server):
#         self.requests.append(server)
#
#     def get_client(self, username):
#         for client in self.clients:
#             if client.get_username() == username:
#                 return client
#         return None
#
#     def get_request(self, request):
#         for r in self.requests:
#             if r == request:
#                 return r
#         return None
#
#     def print_requests(self):
#         for request in self.requests:
#             print(str(request))
