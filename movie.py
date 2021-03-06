# -*- coding: utf-8 -*-

from server_item import ServerList


class Movie:
    """ Stores relevant info about a movie"""
    def __init__(self, id_movie, title, size, path):
        self.id_movie = id_movie
        self.title = title
        self.size = size
        self.path = path

    def to_row(self):
        return [self.id_movie, self.title, self.size, self.path]

    def __str__(self):
        return("id: " + self.id_movie + ", title: " + self.title +
               ", size: " + str(self.size) + ", path: " + self.path)

    def __repr__(self):
        return("Movie(" + self.id_movie + ", " + self.title + ", " +
               str(self.size) + self.path + ")")

    def __eq__(self, other):
        return self.id_movie == other.id_movie

    def __hash__(self):
        return hash((self.id_movie))


class MovieDict:
    """ A dictionary of movies. Type is {Movie, ServerList}"""
    def __init__(self):
        self.movies = {}

    def is_element(self, movie):
        return movie in self.movies

    def is_empty(self):
        return not bool(self.movies)

    def add_movie(self, movie, server):
        if not self.is_element(movie):
            servers = ServerList()
            servers.add_server(server)
            self.movies[movie] = servers
        else:
            self.movies[movie].add_server(server)

    def get_movie(self, id_movie):
        for movie in self.movies:
            if movie.id_movie == id_movie:
                return movie
        return None

    def get_servers(self, movie):
        return self.movies[movie]

    def print_movies(self):
        for movie in self.movies:
            print(str(movie))
            print('server:')
            for server in self.get_servers(movie).get_server_list():
                print(str(server))
            print('---------------------')

    def get_first_download_server(self, movie):
        # Idealmente luego queremos devolver solo un servidor, el ideal
        return self.movies[movie].servers[0]

    def get_best_download_server(self, movie):
        if movie in self.movies:
            selected_server = self.movies[movie].servers[0]
            for server in self.movies[movie].servers:
                if len(selected_server.active_downloads) >= len(server.active_downloads):
                    selected_server = server
            return selected_server
        else:
            return None
