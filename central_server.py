# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Central Server."""

from __future__ import print_function
import signal
from cmd import Cmd
from optparse import OptionParser
from twisted.internet import reactor
from tabulate import tabulate

from central_server_service import ClientService, DownloadServerService
from movie import Movie
import common


class GggomCentralServerShell(Cmd):
    """GGGOM Central Server Shell."""

    intro = (
        'Welcome to the gggom Central Server shell.\n'
        'Type help or ? to list commands.\n'
        'To leave, use exit or ^D.\n')
    prompt = 'GGGOM# '

    def __init__(self, client_service, server_service):
        Cmd.__init__(self)
        self.client_service = client_service
        self.server_service = server_service

    # ======================================================================= #
    # Commands                                                                #
    # ======================================================================= #
    def do_movies_by_server(self, arg):
        """List the available movies by server."""
        args = arg.split()

        if len(args) != 0:
            common.error('`movies_by_server` doesn\'t expect any arguments.')

        else:
            def print_movies_by_server(movies, servers):
                if not servers.is_empty():
                    print("%i available server(s):" % len(
                        servers.get_server_list()))
                    print('')
                    for server in servers.get_server_list():
                        print('server:')
                        print(str(server))
                        print('movies:')
                        if not movies.is_empty():
                            print(tabulate(
                                [movie.to_row() for movie
                                 in movies.get_movie_dict()
                                 if server == movies.get_servers(movie)],
                                headers=['Id', 'Title', 'Size'],
                                tablefmt="psql"))
                            print('')
                        else:
                            print('No movies\n')
                else:
                    print('There\'s no available servers')

            movies, servers = self.server_service.movies_by_server()
            print_movies_by_server(movies, servers)

    def do_downloads_by_server(self, arg):
        """List the movies requested by servers and number of requests."""
        args = arg.split()
        if len(args) != 0:
            common.error('`downloads_by_server` doesn\'t expect any arguments.')
        else:
            print('server 1: fakemovie requested 23 times')

    def do_clients_by_server(self, arg):
        """List the clients handled by each server"""

        args = arg.split()
        if len(args) != 0:
            common.error('`clients_by_server` doesn\'t expect any arguments.')
        else:
            print('server 1: 6 clients')

    def do_exit(self, arg):
        """Stop downloads and exit."""
        return self._leave(arg)

    def do_EOF(self, arg):
        """Stop downloads and exit."""
        print("^D")
        return self._leave(arg)

    # ======================================================================= #
    # Helper Methods                                                          #
    # ======================================================================= #
    def precmd(self, line):
        """Hook method for preprocessing commands.

        This is executed just before the command line is
        interpreted, but after the input prompt is generated and issued.

        """
        if line == "EOF":
            return line
        return line.lower()

    def emptyline(self):
        """Called when an empty line is entered in response to the prompt.

        Does nothing.

        """
        pass

    def _leave(self, arg):
        print('Thank you for using GGGOM.')
        reactor.callFromThread(reactor.stop)
        return True


class CentralServer:
    def __init__(self, client_port, download_port, options):
        self.client_port = client_port
        self.download_port = download_port
        self.options = options
        self.reactor = reactor
        self.client_service = ClientService(self.reactor, self.client_port)
        self.download_service = DownloadServerService(self.reactor,
                                                      self.download_port)
        self.shell = GggomCentralServerShell(self.client_service,
                                             self.download_service)

    def run(self):
        reactor.callInThread(self.shell.cmdloop)
        reactor.run()
