class ServerItem:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.active_downloads = []
        self.finished_downloads = []
        self.downloaded_movies = []

    def __str__(self):
        return '(\'' + self.host + '\', ' + str(self.port) + ')'

    def __eq__(self, other):
        return self.host == other.host and self.port == other.port

    def __hash__(self):
        return ((self.host, self.port))

    def to_server(self):
        return (str(self.host), self.port)

    def add_download(self, request):
        self.active_downloads.append(request)
        exists = False
        for c in self.clients:
            if request.client.username == c[0].username:
                c[1] += 1
                exists = True
        if not exists:
            self.clients.append((request.client, 1))

    def finished_download(self, request):
        if request in self.active_downloads:
            self.active_downloads.remove(request)
            self.finished_downloads.append(request)
        exists = False
        for m in self.downloaded_movies:
            if request.movie.username == m[0].username:
                m[1] += 1
                exists = True
        if not exists:
            self.downloaded_movies.append((request.movie, 1))


class ServerList:
    """ Tiene una lista de servidores """
    def __init__(self):
        self.servers = []

    def is_element(self, server):
        return server in self.servers

    def is_empty(self):
        return not bool(self.servers)

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
