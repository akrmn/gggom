# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies DS Protocols and Factories."""

from __future__ import print_function
from twisted.internet.protocol import ClientFactory as TwistedClientFactory
from twisted.internet.protocol import ServerFactory
from twisted.words.xish.xmlstream import XmlStream
from twisted.internet.defer import Deferred
from twisted.words.xish.domish import Element, IElement
from twisted.python.failure import Failure
from twisted.protocols.basic import LineReceiver

import xml.etree.cElementTree as ET
import os, json

from threading import Lock

from movie import Movie


class RegisterServerProtocol(XmlStream):

    def __init__(self):
        XmlStream.__init__(self)
        self._initializeStream()

    def connectionMade(self):
        request = Element((None, 'register_download_server'))
        request['host'] = self.transport.getHost().host
        request['port'] = str(self.factory.port)
        for movie in self.factory.movies:
            m = request.addElement('movie')
            m['id_movie'] = movie.id_movie
            m['title'] = movie.title
            m['size'] = str(movie.size)
            m['path'] = movie.path
        self.send(request)

    def onDocumentStart(self, elementRoot):
        """ The root tag has been parsed """

        if elementRoot.name == 'registration_reply':
            self.action = 'registration_reply'
            
            if (elementRoot.attributes['reply'] == 'Ok'):
                self.status = 'Ok'
                self.message = elementRoot.attributes['message']
            else:
                self.status = 'Error'
                self.reason = elementRoot.attributes['reason']
                

    def onDocumentEnd(self):
        self.transport.loseConnection()
        if self.status == 'Ok':
            if self.message == "":
                self.factory.deferred.callback('Ok')
            elif self.message == 'already_registered':
                self.factory.deferred.callback('already_registered')
        else:
            self.factory.deferred.errback(Failure(self.reason))

        self.factory.lock.release()

    def register_movies_xml(self):
    	tree = ET.parse('ds_metadata.xml')
        root = tree.getroot()
        movies = root.find('movies')
        for movie in self.factory.movies:
        	ET.SubElement(
            	movies, "movie",
            	id=str(movie.id_movie), size=str(movie.size)).text = movie.title
        tree.write("ds_metadata.xml")


class Register(TwistedClientFactory):

    protocol = RegisterServerProtocol

    def __init__(self, movies, port):
        self.deferred = Deferred()
        self.movies = movies
        self.port = port
        self.lock = Lock()

    def clientConnectionFailed(self, connector, reason):
        self.lock.release()
        self.deferred.errback(reason)


class ClientProtocol(LineReceiver):
    def connectionMade(self):
        pass

    def lineReceived(self, line):
        pass

class ClientListener(ServerFactory):
    """ movie sender factory """
    protocol = ClientProtocol

    def __init__(self, download_server):
        """ """
        self.init = True
        self.download_server = download_server
