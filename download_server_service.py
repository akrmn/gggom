# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Client Service."""

from __future__ import print_function
from download_server_factory import ClientFact, Register


class ClientService:
    def __init__(self, reactor, port):
        self.reactor = reactor
        self.port = int(port)

    def add_movie_list(self, movies):
        self.start_listening(movies)

    def start_listening(self, movies):
        factory = ClientFact(movies)

        self.reactor.callFromThread(
            self.reactor.listenTCP, self.port, factory)

class CentralServerService:
    def __init__(self, reactor, host, port, my_port):
        self.reactor = reactor
        self.host = host
        self.port = port
        self.my_port = int(my_port)

    def register(self, movies, callback, errback):
        factory = Register(movies, self.my_port)
        factory.deferred.addCallbacks(callback, errback)
        factory.lock.acquire()

        self.reactor.callFromThread(
            self.reactor.connectTCP, self.host, self.port, factory)

