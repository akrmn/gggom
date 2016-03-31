# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Client Protocols and Factories."""

from __future__ import print_function
from twisted.internet.protocol import ClientFactory
from twisted.words.xish.xmlstream import XmlStream
from twisted.internet.defer import Deferred
from twisted.words.xish.domish import Element
from twisted.python.failure import Failure
from twisted.protocols.basic import LineReceiver
import json
import os


from threading import Lock

from movie import Movie
from server_item import ServerItem


class RegisterServerProtocol(XmlStream):

    def __init__(self):
        XmlStream.__init__(self)
        self._initializeStream()

    def connectionMade(self):
        request = Element((None, 'register_client'))
        request['host'] = self.transport.getHost().host
        request['port'] = str(self.transport.getHost().port)
        request.addElement('username').addContent(self.factory.username)
        self.send(request)

    def onDocumentStart(self, elementRoot):
        """ The root tag has been parsed """
        if elementRoot.name == 'registration_reply':
            if elementRoot.attributes['reply'] == 'Ok':
                self.factory.deferred.callback('Ok')
            else:
                self.factory.deferred.errback(
                    Failure(elementRoot.attributes['reason']))
        self.factory.lock.release()


class Register(ClientFactory):

    protocol = RegisterServerProtocol

    def __init__(self, username):
        self.deferred = Deferred()
        self.username = username
        self.lock = Lock()

    def clientConnectionFailed(self, connector, reason):
        self.deferred.errback(reason)
        self.lock.release()


class ListMovieServerProtocol(XmlStream):

    def __init__(self):
        XmlStream.__init__(self)
        self._initializeStream()
        self.movies = []

    def connectionMade(self):
        request = Element((None, 'list_movies'))
        self.send(request)

    def onDocumentStart(self, elementRoot):
        """ The root tag has been parsed """
        if elementRoot.name == 'movie_list':
            self.action = 'movie_list'

    def onElement(self, element):
        """ Children/Body elements parsed """
        if element.name == 'movie':
            id_movie = str(element.attributes['id_movie'])
            title = str(element.attributes['title'])
            size = int(element.attributes['size'])
            self.movies.append(Movie(id_movie, title, size))

    def onDocumentEnd(self):
        """ Parsing has finished, you should send your response now """
        if self.action == 'movie_list':
            self.factory.deferred.callback(self.movies)
            self.factory.lock.release()


class ListMovies(ClientFactory):

    protocol = ListMovieServerProtocol

    def __init__(self):
        self.deferred = Deferred()
        self.lock = Lock()

    def clientConnectionFailed(self, connector, reason):
        self.deferred.errback(reason)
        self.lock.release()


class DownloadMovieCentralServerProtocol(XmlStream):

    def __init__(self):
        XmlStream.__init__(self)
        self._initializeStream()
        self.download_server = None

    def connectionMade(self):
        request = Element((None, 'request_movie'))
        request.addElement('username').addContent(self.factory.username)
        request.addElement('id_movie').addContent(self.factory.id_movie)
        self.send(request)

    def onDocumentStart(self, elementRoot):
        """ The root tag has been parsed """
        self.action = elementRoot.name

    def onElement(self, element):
        """ Children/Body elements parsed """
        if element.name == 'server':
            host = str(element.attributes['host'])
            port = int(element.attributes['port'])
            self.download_server = ServerItem(host, port)

    def onDocumentEnd(self):
        """ Parsing has finished, you should send your response now """
        if self.action == 'download_from':
            self.factory.deferred.callback(self.download_server)
            self.factory.lock.release()
        elif self.action == 'unavailable':
            self.factory.deferred.errback(
                Exception('No server available for download'))
            self.factory.lock.release()

    def closeConnection(self):
        self.transport.loseConnection()

    def connectionLost(self, reason):
        self.closeConnection()


class DownloadMovie(ClientFactory):

    protocol = DownloadMovieCentralServerProtocol

    def __init__(self, username, id_movie):
        self.deferred = Deferred()
        self.id_movie = id_movie
        self.username = username
        self.lock = Lock()

    def clientConnectionFailed(self, connector, reason):
        self.deferred.errback(reason)
        self.lock.release()


class FetchMovieProtocol(LineReceiver):
    """ Movie Receiver """

    def lineReceived(self, line):
        """ """
        print(line)


    def connectionMade(self):
        """ """
        pass

class FetchMovie(ClientFactory):
    """ Movie receiver factory """
    protocol = FetchMovieProtocol

    def __init__(self, username, movie, server):
        """ """

        self.deferred = Deferred()
        self.username = username
        self.movie = movie
        self.download_server = server
        self.lock = Lock()

    def clientConnectionFailed(self, connector, reason):
        self.deferred.errback(reason)
        self.lock.release()
