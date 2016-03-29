# coding=utf-8
from server_item import ServerList


class Movie:
    """ Stores relevant info about a movie"""
    def __init__(self, id_movie, title, size):
        self.id_movie = id_movie
        self.title = title
        self.size = size

    def to_row(self):
        return [self.id_movie, self.title, self.size]

    def __str__(self):
        return("id: " + self.id_movie + ", title: " + self.title +
               ", size: " + str(self.size))

    def __repr__(self):
        return("Movie(" + self.id_movie + ", " + self.title + ", " +
               str(self.size) + ")")


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
            self.movies[movie] = ServerList().add_server(server)
        else:
            self.movies[movie].add_server(server)

    def get_movie(self, id_movie):
        for movie in self.movies:
            if movie.get_id() == id_movie:
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

    def get_download_server_list(self, movie):
        # Idealmente luego queremos devolver solo un servidor, el ideal
        return self.get_servers(movie).get_server_list()
