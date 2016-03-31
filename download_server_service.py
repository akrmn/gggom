# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Download Server Services."""

from __future__ import print_function
from download_server_factory import Register, ClientListener


class ClientService:
    def __init__(self, download_server):
        self.reactor = download_server.reactor
        self.port = int(download_server.client_port)
        self.download_server = download_server
        self.start_listening()

    def start_listening(self):
        factory = ClientListener(self.download_server)

        self.reactor.callFromThread(
            self.reactor.listenTCP, self.port, factory)


class CentralServerService:
    def __init__(self, download_server):
        self.reactor = download_server.reactor
        self.host = download_server.host
        self.port = download_server.port
        self.my_port = int(download_server.client_port)
        self.download_server = download_server

    def register(self, callback, errback):
        factory = Register(self.download_server.movies, self.my_port)
        factory.deferred.addCallbacks(callback, errback)
        factory.lock.acquire()

        self.reactor.callFromThread(
            self.reactor.connectTCP, self.host, self.port, factory)
