# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Client Service."""

from __future__ import print_function
from factory import Register, ListMovies


class ClientService:
    def __init__(self, reactor, host, port):
        self.reactor = reactor
        self.host = host
        self.port = port

    def register(self, username, callback, errback):
        factory = Register(username)
        factory.deferred.addCallbacks(callback, errback)
        factory.lock.acquire()

        self.reactor.callFromThread(
            self.reactor.connectTCP, self.host, self.port, factory)

        factory.lock.acquire()

    def list_movies(self, callback, errback):
        factory = ListMovies()
        factory.deferred.addCallbacks(callback, errback)
        factory.lock.acquire()

        self.reactor.callFromThread(
            self.reactor.connectTCP, self.host, self.port, factory)

        factory.lock.acquire()
