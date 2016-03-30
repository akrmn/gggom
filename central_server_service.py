# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Central Server Services."""

from __future__ import print_function
from central_server_factory import ClientFactory, DownloadServerFactory


class ClientService:
    def __init__(self, central_server):
        self.central_server = central_server
        self.start_listening()

    def start_listening(self):
        self.factory = ClientFactory(self.central_server)

        self.central_server.reactor.callFromThread(
            self.central_server.reactor.listenTCP,
            self.central_server.client_port, self.factory)

    def get_clients(self):
        return self.central_server.clients

    def get_movies(self):
        return self.central_server.movies

    def get_servers(self):
        return self.central_server.servers

    def get_requests(self):
        return self.central_server.requests


class DownloadServerService:
    def __init__(self, central_server):
        self.central_server = central_server
        self.start_listening()

    def start_listening(self):
        self.factory = DownloadServerFactory(self.central_server)

        self.central_server.reactor.callFromThread(
            self.central_server.reactor.listenTCP,
            self.central_server.download_port, self.factory)

    def get_clients(self):
        return self.central_server.clients

    def get_movies(self):
        return self.central_server.movies

    def get_servers(self):
        return self.central_server.servers

    def get_requests(self):
        return self.central_server.requests

    def movies_by_server(self):
        return self.central_server.movies, self.central_server.servers
