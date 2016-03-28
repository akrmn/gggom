# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Client Service."""

from __future__ import print_function
from central_server_factory import ClientFact


class ClientService:
    def __init__(self, reactor, host, port):
        self.reactor = reactor
        self.host = host
        self.port = port
        self.start_listening()

    def start_listening(self):
        factory = ClientFact()

        self.reactor.callFromThread(
            self.reactor.listenTCP, self.port, factory)
