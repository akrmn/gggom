# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Central Server."""

from __future__ import print_function
from cmd import Cmd
from twisted.internet import reactor
from tabulate import tabulate

from central_server_service import ClientService, DownloadServerService
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
                        servers.servers))
                    print('')
                    for server in servers.servers:
                        print('server:')
                        print(str(server))
                        print('movies:')
                        if not movies.is_empty():
                            print(tabulate(
                                [movie.to_row() for movie
                                 in movies.movies
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
            common.error('`downloads_by_server` doesn\'t'
                         'expect any arguments.')
        else:
            def print_downloads_by_server(servers, downloads):
                if not servers.is_empty():
                    print("%i server(s):" % len(
                        servers.servers))
                    print('')
                    for server in servers.servers:
                        print('server:')
                        print(str(server))
                        print('downloads:')
                        if not requests.is_empty():
                            print(tabulate(
                                [requests.to_row() for request
                                 in requests.requests
                                 if server == request.server],
                                headers=['Movie', 'Server', 'Client'],
                                tablefmt="psql"))
                            print('')
                        else:
                            print('No downloads\n')
                else:
                    print('There\'s no available servers')

            servers = self.server_service.get_servers()
            requests = self.client_service.get_requests()
            print_downloads_by_server(servers, requests)

    def do_clients_by_server(self, arg):
        """List the clients handled by each server"""

        args = arg.split()
        if len(args) != 0:
            common.error('`clients_by_server` doesn\'t expect any arguments.')
        else:
            def print_clients_by_server(servers, downloads):
                if not servers.is_empty():
                    print("%i server(s):" % len(
                        servers.servers))
                    print('')
                    for server in servers.servers:
                        print('server:')
                        print(str(server))
                        print('downloads:')
                        if not requests.is_empty():
                            print(tabulate(
                                [requests.client for request
                                 in requests.requests
                                 if server == request.server],
                                headers=['Client'],
                                tablefmt="psql"))
                            print('')
                        else:
                            print('No clients\n')
                else:
                    print('There\'s no available servers')

            servers = self.server_service.get_servers()
            requests = self.client_service.get_requests()
            print_clients_by_server(servers, requests,)

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
