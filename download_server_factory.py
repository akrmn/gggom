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

# class ClientProtocol(XmlStream):

#     def __init__(self):
#         XmlStream.__init__(self)
#         self._initializeStream()

#     def onDocumentStart(self, elementRoot):
#         """ The root tag has been parsed """
#         if elementRoot.name == 'request_movie':
#             self.action = 'request_movie'

#     def onElement(self, element):
#         """ Children/Body elements parsed """
#         if element.name == 'id_movie':
#             self.id_movie = str(element)

#     def onDocumentEnd(self):
#         """ Parsing has finished, you should send your response now """
#         if self.action == 'request_movie':
#             self.send_movie(self.id_movie)

#     def send_movie(self, movie):
#         if self.factory.movies.is_element(movie):
#             reply = Element((None, 'movie_download'))
#             self.send(reply)
#         else:
#             reply = Element((None, 'no_movie'))
#             self.send(reply)

#     def list_movies(self):
#         reply = Element((None, 'movie_list'))
#         for movie in self.factory.movies.get_movie_dict():
#             m = reply.addElement('movie')
#             m['id_movie'] = movie.id_movie
#             m['title'] = movie.title
#             m['size'] = str(movie.size)
#         self.send(reply)

#     def closeConnection(self):
#         self.transport.loseConnection()

#     def connectionMade(self):
#         print('Nueva conexión desde', self.transport.getPeer())


# class ClientFactory(TwistedClientFactory):

#     protocol = ClientProtocol

#     def __init__(self, movies):
#         self.deferred = Deferred()
#         self.lock = Lock()
#         self.movies = movies


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
                self.factory.deferred.callback('Ok')
            else:
                self.factory.deferred.errback(
                    Failure(elementRoot.attributes['reason']))
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
        self.deferred.errback(reason)
        self.lock.release()


class ClientProtocol(XmlStream):
# class ClientProtocol(LineReceiver):
    def __init__(self):
        """ """
        XmlStream.__init__(self)
        self._initializeStream()

        # self.infile = open(self.path, 'rb')
        # self.insize = os.stat(self.path).st_size
        # self.result = None
        # self.completed = False

    def onDocumentStart(self, elementRoot):
        """ The root tag has been parsed """
        if elementRoot.name == 'register_download_server':
            self.action = 'register_download_server'
            self.host = str(elementRoot.attributes['host'])
            self.port = int(elementRoot.attributes['port'])
        else:
            print("WOO")

    # # def cbTransferCompleted(self):
    # #     """ """
    # #     self.completed = True
    # #     self.transport.loseConnection()

    # def lineReceived(self, line):
    #     print(line)

    # def connectionMade(self):
    #     """ """
    #     print("I HAVE BEEN CONNECTED TO SOMEONE")
    #     # instruction = dict(file_size=self.insize,
    #     #                    original_file_name=os.path.basename(self.path))
    #     # instruction = json.dumps(instruction)
    #     # self.transport.write(instruction + '\r\n')
    #     # sender = basic.FileSender()
    #     # d = sender.beginFileTransfer(self.infile, self.transport,
    #     #                              self._monitor)
    #     # d.addCallback(self.cbTransferCompleted)

    # # def connectionLost(self, reason):
    # #     """
    # #         NOTE: reason is a twisted.python.failure.Failure instance
    # #     """
    # #     basic.LineReceiver.connectionLost(self, reason)
    # #     print(' - connectionLost\n  * ', reason.getErrorMessage())
    # #     self.infile.close()
    # #     if self.completed:
    # #         self.controller.completed.callback(self.result)
    # #     else:
    # #         self.controller.completed.errback(reason)


class ClientListener(ServerFactory):
    """ movie sender factory """
    protocol = ClientProtocol

    def __init__(self, download_server):
        """ """
        self.init = True
        self.download_server = download_server

