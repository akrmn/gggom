# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Client Service."""

from __future__ import print_function
from client_factory import Register, ListMovies, DownloadMovie, FetchMovie


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

    def download(self, username, movie, callback, errback):
        factory = DownloadMovie(username, movie)
        factory.deferred.addCallbacks(callback, errback)
        factory.lock.acquire()

        self.reactor.callFromThread(
            self.reactor.connectTCP, self.host, self.port, factory)

        factory.lock.acquire()

    def start_fetch(self, username, movie, server, callback, errback):
        factory = FetchMovie(username, movie, server)
        factory.deferred.addCallbacks(callback, errback)
        factory.lock.acquire()

        self.reactor.callFromThread(
            self.reactor.connectTCP, server.host, server.port, factory)

        factory.lock.acquire()
