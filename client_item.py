class ClientItem:

    def __init__(self, username, host, port):
        self.username = username
        self.host = host
        self.port = port

    def __str__(self):
        return self.username + ' ' + self.host + ' ' + str(self.port)

    def __eq__(self, other):
        return self.username == other.username


# class ClientDict:
#     """ A dictionary of clients. Type is {ClientItem, RequestList}"""
#     def __init__(self):
#         self.clients = {}
#
#     def is_element(self, client):
#         return client in self.clients
#
#     def add_client(self, client, request=None):
#         """Adds a client if it doesn't exist, if it does exist it adds a new
#         request to it. Returns None when the client exists and we're not
#         adding a new request to it"""
#         if request is not None:
#             if not self.is_element(client):
#                 self.clients[client] = RequestList()
#             else:
#                 self.clients[client].add_request(request)
#             return client
#         else:
#             if not self.is_element(client):
#                 self.clients[client] = RequestList()
#                 return client
#             else:
#                 return None
#
#     def get_client_dict(self):
#         return self.clients
#
#     def get_requests(self, client):
#         return self.clients[client]
#
#     def print_clients(self):
#         for client in self.clients:
#             print(str(client))
#             print('request:')
#             for request in self.get_requests().get_request_list():
#                 print(request)
#             print('---------------------')
#
#     def get_request_list(self, movie):
#         # Idealmente luego queremos devolver solo un servidor, el ideal
#         return self.get_requests().get_request_list()