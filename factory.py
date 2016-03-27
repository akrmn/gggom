# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Protocols and Factories."""

from twisted.internet.protocol import ClientFactory
from twisted.words.xish.xmlstream import XmlStream
from twisted.internet.defer import Deferred
from twisted.words.xish.domish import Element, IElement

class RegisterServerProtocol(XmlStream):

    def __init__(self):
        XmlStream.__init__(self)    # possibly unnecessary
        self._initializeStream()

    def sendObject(self, obj):
        # if IElement.providedBy(obj):
        #     print("[TX]: %s" % obj.toXml())
        # else:
        #     print("[TX]: %s" % obj)
        self.send(obj)

    def connectionMade(self):
        request = Element((None, 'register_client'))
        request['host'] = self.transport.getHost().host
        request['port'] = str(self.transport.getHost().port)
        request.addElement('username').addContent(self.factory.username)
        self.sendObject(request)

    def dataReceived(self, data):
        """ Overload this function to simply pass the incoming data into the XML parser """
        print("RSP data received")

        try:
            self.stream.parse(data)
        except Exception as e:
            self._initializeStream()

    def onDocumentStart(self, elementRoot):
        """ The root tag has been parsed """
        print('Root tag: {0}'.format(elementRoot.name))
        print('Attributes: {0}'.format(elementRoot.attributes))
        if elementRoot.name == 'registration_reply':
            self.action = 'registration_reply'
            if (elementRoot.attributes['reply'] == 'Ok'):
                print('Se registró exitosamente en el servidor central')
            else:
                print('No se registró en el servidor central')

    def onElement(self, element):
        """ Children/Body elements parsed """
        print('\nElement tag: {0}'.format(element.name))
        print('Element attributes: {0}'.format(element.attributes))
        print('Element content: {0}'.format(element))

    def onDocumentEnd(self):
        """ Parsing has finished, you should send your response now """

class Register(ClientFactory):

    protocol = RegisterServerProtocol

    def __init__(self, username):
        self.deferred = Deferred()
        self.username = username

    def reply_received(self, reply):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(reply)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason + connector.getDestination())
