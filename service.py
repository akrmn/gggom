# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Client Service."""

from factory import Register

class ClientService:
    def __init__(self, reactor, host, port):
        self.reactor = reactor
        self.host = host
        self.port = port

    def register(self, username):
        factory = Register(username)
        factory.deferred.addCallback(self.print_confirmation)
        self.reactor.callFromThread(
            self.reactor.connectTCP, self.host, self.port, factory)
        return factory.deferred

    def list_movies(self):
        factory = ListMovieServerFactory()
        factory.deferred.addCallback(self.print_movie_list)
        self.reactor.connectTCP(self.host, self.port, factory)
        return factory.deferred

    def request_movie(self, movie):
        factory = RequestMovieCentralServerFactory(movie)
        factory.deferred.addCallback(self.print_ok)
        self.reactor.connectTCP(self.host, self.port, factory)
        return factory.deferred

    def print_confirmation(self, reply):
        return reply

    def print_movie_list(self, movies):
        print('')
        print('Peliculas del servidor:')
        print('----------------------------------------')
        for movie in movies:
            print(movie.to_string())
            print('----------------------------------------')

    def receiving_movie(self, id_movie):
        print('Recibiendo pelicula', id_movie)
        return 'Recibiendo pelicula' + id_movie

    def print_ok(self):
        print('Ok')
        return 'Ok'

    def get_movie_from_server(self, id_movie, server):
        print('Buscando la pelicula', id_movie, 'en el servidor', server.to_string())
        return 'Buscando la pelicula' + id_movie + 'en el servidor' + server.to_string()
        #print('SONIAAA ESTAS AHI?'
        #print(server.to_string()
        #factory = RequestMovieDownloadServerFactory(id_movie, server)
        #factory.deferred.addCallback(self.receiving_movie)
        #from twisted.internet import reactor
        #print(server.to_string()
        #reactor.connectTCP(server.host, server.port, factory)
        #return factory.deferred
