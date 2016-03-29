# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies CS Protocols and Factories."""

from __future__ import print_function
from twisted.internet.protocol import ClientFactory as TwistedClientFactory
from twisted.internet.protocol import ServerFactory
from twisted.words.xish.xmlstream import XmlStream
from twisted.internet.defer import Deferred
from twisted.words.xish.domish import Element

from threading import Lock

from movie import Movie, MovieDict
from server_item import ServerItem, ServerList
from client_item import ClientItem, ClientDict
from request import RequestList


class ClientProtocol(XmlStream):

    def __init__(self):
        XmlStream.__init__(self)    # possibly unnecessary
        self._initializeStream()
        # FIXME: dummy movie list, it has to be changed later
        self.movies = MovieDict()
        self.movies.add_movie(Movie('fakeone',
                                    "Harry Potter and the Fakey Fake", 35),
                              ServerItem('192.168.1.1', 10004))
        self.movies.add_movie(Movie('phoney',
                                    "Draco Malfoy and the Dark Lord", 35),
                              ServerItem('192.168.1.2', 10006))

    def onDocumentStart(self, elementRoot):
        """ The root tag has been parsed """
        if elementRoot.name == 'register_client':
            self.action = 'register_client'
            self.host = str(elementRoot.attributes['host'])
            self.port = int(elementRoot.attributes['port'])
        elif elementRoot.name == 'list_movies':
            self.action = 'list_movies'

    def onElement(self, element):
        """ Children/Body elements parsed """
        if element.name == 'username':
            self.username = str(element)
        elif element.name == 'id_movie':
            self.id_movie = str(element)

    def onDocumentEnd(self):
        """ Parsing has finished, you should send your response now """
        if self.action == 'register_client':
            self.client = ClientItem(self.username, self.host, self.port)
            result = self.factory.clients.add_client(self.client)
            if result is None:
                print('Client ', str(self.client), 'is already registered.')
                self.registration_failed('Client already registered')
            else:
                print('Se agregó el nuevo cliente: ', self.client)
                self.registration_ok()
        elif self.action == 'list_movies':
            self.list_movies()

    def list_movies(self):
        request = Element((None, 'movie_list'))
        for movie in self.factory.movies.movies:
            m = request.addElement('movie')
            m['id_movie'] = movie.id_movie
            m['title'] = movie.title
            m['size'] = str(movie.size)
        self.send(request)

    def registration_ok(self):
        response = Element((None, 'registration_reply'))
        response['reply'] = 'Ok'
        self.send(response)

    def registration_failed(self, reason):
        response = Element((None, 'registration_reply'))
        response['reply'] = 'Failed'
        response['reason'] = reason
        self.send(response)


class ClientFactory(TwistedClientFactory):

    protocol = ClientProtocol

    def __init__(self):
        self.deferred = Deferred()
        self.lock = Lock()
        self.clients = ClientDict()

        self.movies = MovieDict()
        self.requests = RequestList()
        # This movie list is saved on the download server factory, it should
        # maybe even be saved in the Cmd, I don't know how to access that from
        # here. This is a temporal fix
        self.movies.add_movie(Movie('fakeone',
                                    "Harry Potter and the Fakey Fake", 35),
                              None)
        self.movies.add_movie(Movie('phoney',
                                    "Draco Malfoy and the Dark Lord", 35),
                              None)


class DownloadServerProtocol(XmlStream):

    def __init__(self):
        XmlStream.__init__(self)    # possibly unnecessary
        self._initializeStream()
        self.movie_list = []

    def onDocumentStart(self, elementRoot):
        """ The root tag has been parsed """
        if elementRoot.name == 'register_download_server':
            self.action = 'register_download_server'
            self.host = str(elementRoot.attributes['host'])
            self.port = int(elementRoot.attributes['port'])

    def onElement(self, element):
        """ Children/Body elements parsed """
        if element.name == 'movie':
            id_movie = str(element.attributes['id_movie'])
            title = str(element.attributes['title'])
            size = int(element.attributes['size'])
            self.movie_list.append(Movie(id_movie, title, size))

    def onDocumentEnd(self):
        """ Parsing has finished, you should send your response now """
        if self.action == 'register_download_server':
            self.server = ServerItem(self.host, self.port)
            self.add_movie_list()
            result = self.factory.servers.add_server(self.server)
            if result is not None:
                print('Server', str(self.server), 'was added to the list')
                self.registration_ok()
            else:
                print('Server', str(self.server), 'is already registered')
                self.registration_failed('Server already registered')

    def registration_ok(self):
        response = Element((None, 'registration_reply'))
        response['reply'] = 'Ok'
        self.send(response)

    def registration_failed(self, reason):
        response = Element((None, 'registration_reply'))
        response['reply'] = 'Failed'
        response['reason'] = reason
        self.send(response)

    def add_movie_list(self):
        for movie in self.movie_list:
            self.factory.movies.add_movie(movie, self.server)

    def closeConnection(self):
        self.transport.loseConnection()

    def print_movie_list(self):
        self.factory.movies.print_movies()


class DownloadServerFactory(ServerFactory):

    protocol = DownloadServerProtocol

    def __init__(self):
        self.init = True
        self.movies = MovieDict()
        self.servers = ServerList()
