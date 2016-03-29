# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Central Server Services."""

from __future__ import print_function
from central_server_factory import ClientFactory, DownloadServerFactory


class ClientService:
    def __init__(self, reactor, port):
        self.reactor = reactor
        self.port = int(port)
        self.start_listening()

    def start_listening(self):
        self.factory = ClientFactory()

        self.reactor.callFromThread(
            self.reactor.listenTCP, self.port, self.factory)

    def get_requests(self):
        return self.factory.requests


class DownloadServerService:
    def __init__(self, reactor, port):
        self.reactor = reactor
        self.port = int(port)
        self.start_listening()

    def start_listening(self):
        self.factory = DownloadServerFactory()

        self.reactor.callFromThread(
            self.reactor.listenTCP, self.port, self.factory)

    def movies_by_server(self):
        return self.factory.movies, self.factory.servers

    def get_servers(self):
        return self.factory.servers
