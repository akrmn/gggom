# coding=utf-8
class Movie:
    """ Stores relevant info about a movie"""
    def __init__(self, id_movie, title, size):
        self.id_movie = id_movie
        self.title = title
        self.size = size

    def get_id(self):
        return self.id_movie

    def get_title(self):
        return self.title

    def get_size(self):
        return self.size

    def __str__(self):
        return("id: " + self.id_movie + ", title: " + self.title +
               ", size: " + str(self.size))

    def __repr__(self):
        return("Movie(" + self.id_movie + ", " + self.title + ", " +
               str(self.size) + ")")

    def to_row(self):
        return [self.id_movie, self.title, self.size]


class MovieDict:
    """ A dictionary of movies. Type is {Movie, ServerList}"""
    def __init__(self):
        self.movies = {}

    def is_element(self, movie):
        return movie in self.movies

    def is_empty(self):
        if self.movies:
            return False
        else:
            return True

    def add_movie(self, movie, server):
        if not self.is_element(movie):
            self.movies[movie] = ServerList().add_server(server)
        else:
            self.movies[movie].add_server(server)

    def get_movie_dict(self):
        return self.movies

    def get_movie(self, id_movie):
        for movie in self.movies:
            if movie.get_id() == id_movie:
                return movie
        return None

    def get_servers(self, movie):
        return self.movies[movie]

    def print_movies(self):
        for movie in self.movies:
            print(str(movie))
            print('server:')
            for server in self.get_servers(movie).get_server_list():
                print(str(server))
            print('---------------------')

    def get_download_server_list(self, movie):
        # Idealmente luego queremos devolver solo un servidor, el ideal
        return self.get_servers(movie).get_server_list()


class Client:

    def __init__(self, username, host, port):
        self.username = username
        self.host = host
        self.port = port

    def get_username(self):
        return self.username

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def __str__(self):
        return self.username + ' ' + self.host + ' ' + str(self.port)

    def is_equal(self, client):
        return self.username == client.username


class ClientDict:
    """ A dictionary of clients. Type is {Client, RequestList}"""
    def __init__(self):
        self.clients = {}

    def is_element(self, client):
        return client in self.clients

    def add_client(self, client, request=None):
        """Adds a client if it doesn't exist, if it does exist it adds a new
        request to it. Returns None when the client exists and we're not
        adding a new request to it"""
        if request is not None:
            if not self.is_element(client):
                self.clients[client] = RequestList()
            else:
                self.clients[client].add_request(request)
            return client
        else:
            if not self.is_element(client):
                self.clients[client] = RequestList()
                return client
            else:
                return None

    def get_client_dict(self):
        return self.clients

    def get_requests(self, client):
        return self.clients[client]

    def print_clients(self):
        for client in self.clients:
            print(str(client))
            print('request:')
            for request in self.get_requests().get_request_list():
                print(request)
            print('---------------------')

    def get_request_list(self, movie):
        # Idealmente luego queremos devolver solo un servidor, el ideal
        return self.get_requests().get_request_list()


class Server:

    def __init__(self, host, port, clients=[], active_downloads=[],
                 finished_downloads=[], downloaded_movies=[]):
        self.host = host
        self.port = port
        self.clients = clients
        self.active_downloads = active_downloads
        self.finished_downloads = finished_downloads
        self.downloaded_movies = downloaded_movies

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def __str__(self):
        return '(\'' + self.host + '\', ' + str(self.port) + ')'

    def to_server(self):
        return (str(self.host), self.port)

    def add_download(self, client, movie):
        self.active_downloads.append((client, movie))
        exists = False
        for c in self.clients:
            if client == c[0]:
                c[1] += 1
                exists = True
        if not exists:
            self.clients.append((client, 1))

    def finished_download(self, client, movie):
        if (client, movie) in self.active_downloads:
            self.active_downloads.remove((client, movie))
            self.finished_downloads.append((client, movie))
        exists = False
        for m in self.downloaded_movies:
            if movie in m[0]:
                m[1] += 1
                exists = True
        if not exists:
            self.downloaded_movies.append((movie, 1))


class ServerList:
    """ Tiene una lista de servidores """
    def __init__(self):
        self.servers = []

    def is_element(self, server):
        return server in self.servers

    def is_empty(self):
        if self.servers:
            return False
        else:
            return True

    def add_server(self, server):
        if not self.is_element(server):
            self.servers.append(server)
            return server
        else:
            return None

    def get_server_list(self):
        return self.servers

    def get_server_with_host(self, host, port):
        for server in self.servers:
            if server.get_host() == host and server.get_port() == port:
                return server
        return None

    def get_server(self, server):
        for s in self.servers:
            if s == server:
                return s
        return None

    def print_servers(self):
        for server in self.servers:
            print(str(server))


class Request:

    def __init__(self, movie, server):
        self.movie = movie
        self.server = server

    def __str__(self):
        return('request: movie:' + str(self.movie) + ', server:' +
               str(self.server))


class RequestList:
    """ Tiene una lista de requests """
    def __init__(self):
        self.requests = []

    def is_element(self, request):
        return request in self.requests

    def add_request(self, server):
        self.requests.append(server)

    def get_client(self, username):
        for client in self.clients:
            if client.get_username() == username:
                return client
        return None

    def get_request_list(self):
        return self.requests

    def get_request(self, request):
        for r in self.requests:
            if r == request:
                return r
        return None

    def print_requests(self):
        for request in self.requests:
            print(str(request))
