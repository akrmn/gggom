# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies CS Protocols and Factories."""

from __future__ import print_function
from twisted.internet.protocol import ClientFactory as TwistedClientFactory
from twisted.internet.protocol import ServerFactory
from twisted.words.xish.xmlstream import XmlStream
from twisted.internet.defer import Deferred
from twisted.words.xish.domish import Element

from threading import Lock

from movie import Movie
from server_item import ServerItem
from client_item import ClientItem
from request import Request


class ClientProtocol(XmlStream):

    def __init__(self):
        XmlStream.__init__(self)    # possibly unnecessary
        self._initializeStream()

    def onDocumentStart(self, elementRoot):
        """ The root tag has been parsed """
        if elementRoot.name == 'register_client':
            self.action = 'register_client'
            self.host = str(elementRoot.attributes['host'])
            self.port = int(elementRoot.attributes['port'])
        elif elementRoot.name == 'list_movies':
            self.action = 'list_movies'
        elif elementRoot.name == 'request_movie':
            self.action = 'request_movie'

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
            result = self.factory.central_server.clients.add_client(self.client)
            if result is None:
                print('Client ', str(self.client), 'is already registered.')
                self.registration_failed('Client already registered')
            else:
                print('Se agregó el nuevo cliente: ', self.client)
                self.registration_ok()
        elif self.action == 'list_movies':
            self.list_movies()
        elif self.action == 'request_movie':
            self.choose_download_server(self.id_movie)

    def choose_download_server(self, movie):
        mov = self.factory.central_server.movies.get_movie(movie)
        # Ahorita solo elegimos el primero de la lista, idealmente queremos el
        # que sea el mejor, no el primero
        download_server = self.factory.central_server.movies.get_first_download_server(mov)
        request = Element((None, 'download_from'))
        s = request.addElement('server')
        s['host'] = download_server.host
        s['port'] = str(download_server.port)
        client = self.factory.central_server.clients.get_client(self.username)
        req = Request(mov, download_server, client)
        self.factory.central_server.clients.add_client(client, req)
        server = self.factory.central_server.servers.get_server(download_server)
        server.add_download(req)
        self.factory.central_server.requests.add_request(req)
        for s in self.factory.central_server.servers.servers:
            print(id(s))
            print('req:')
            for r in s.active_downloads:
                print(r)
        self.send(request)

    def list_movies(self):
        request = Element((None, 'movie_list'))
        for movie in self.factory.central_server.movies.movies:
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

    def __init__(self, central_server):
        self.deferred = Deferred()
        self.lock = Lock()
        self.central_server = central_server


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
            result = self.factory.central_server.servers.add_server(self.server)
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
            self.factory.central_server.movies.add_movie(movie, self.server)

    def closeConnection(self):
        self.transport.loseConnection()

    def print_movie_list(self):
        self.factory.central_server.movies.print_movies()


class DownloadServerFactory(ServerFactory):

    protocol = DownloadServerProtocol

    def __init__(self, central_server):
        self.init = True
        self.central_server = central_server
