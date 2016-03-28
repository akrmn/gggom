# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Protocols and Factories."""

from __future__ import print_function
from twisted.internet.protocol import ClientFactory, ServerFactory
from twisted.words.xish.xmlstream import XmlStream
from twisted.internet.defer import Deferred
from twisted.words.xish.domish import Element, IElement
from twisted.python.failure import Failure

from threading import Lock

from movie import Movie, MovieList, Client, ClientList, Server, ServerList


class ClientProtocol(XmlStream):

    def __init__(self):
        XmlStream.__init__(self)    # possibly unnecessary
        self._initializeStream()
        # FIXME: dummy movie list, it has to be changed later
        self.movies = MovieList()
        self.movies.add_movie(Movie('fakeone', "Harry Potter and the Fakey Fake", 35), Server('192.168.1.1', 10004))
        self.movies.add_movie(Movie('phoney', "Draco Malfoy and the Dark Lord", 35), Server('192.168.1.2', 10006))

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
            self.client = Client(self.username, self.host, self.port)
            result = self.factory.clients.add_client(self.client)
            if result is None:
                print('Client ', self.client.to_string(), 'is already registered.')
                self.registration_failed('Client already registered')
            else:
                print('Se agregó el nuevo cliente: ', self.client.to_string())
                self.registration_ok()
        elif self.action == 'list_movies':
            self.list_movies()

    def list_movies(self):
        request = Element((None, 'movie_list'))
        for movie in self.factory.movies.get_movie_dict():
            m = request.addElement('movie')
            m['id_movie'] = movie.get_id()
            m['title'] = movie.get_title()
            m['size'] = str(movie.get_size())
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

class ClientFact(ClientFactory):

    protocol = ClientProtocol

    def __init__(self):
        self.deferred = Deferred()
        self.lock = Lock()
        self.clients = ClientList()


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
            m = Movie(id_movie, title, size)
            self.movie_list.append(Movie(id_movie, title, size))

    def onDocumentEnd(self):
        """ Parsing has finished, you should send your response now """
        if self.action == 'register_download_server':
            self.server = Server(self.host, self.port)
            self.add_movie_list()
            result = self.factory.servers.add_server(self.server)
            if result is not None:
                print('Server', self.server.to_string(), 'was added to the list')
                self.registration_ok()
            else:
                print('Server', self.server.to_string(), 'is already registered')
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
        self.movies = MovieList()
        self.servers = ServerList()
