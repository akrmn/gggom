# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Central Server."""

from __future__ import print_function
from cmd import Cmd
from twisted.internet import reactor
from tabulate import tabulate

from central_server_service import ClientService, DownloadServerService

from client_item import ClientDict
from movie import MovieDict
from request import RequestList
from server_item import ServerList

import common


class GggomCentralServerShell(Cmd):
    """GGGOM Central Server Shell."""

    intro = (
        'Welcome to the gggom Central Server shell.\n'
        'Type help or ? to list commands.\n'
        'To leave, use exit or ^D.\n')
    prompt = 'GGGOM# '

    def __init__(self, central_server):
        Cmd.__init__(self)
        self.central_server = central_server

    # ======================================================================= #
    # Commands                                                                #
    # ======================================================================= #
    def do_movies_by_server(self, arg):
        """List the available movies by server."""
        args = arg.split()

        if len(args) != 0:
            common.error('`movies_by_server` doesn\'t expect any arguments.')

        else:
            movies, servers = \
                self.central_server.download_service.movies_by_server()
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
                             if server in movies.get_servers(movie).servers],
                            headers=['Id', 'Title', 'Size'],
                            tablefmt="psql"))
                        print('')
                    else:
                        print('No movies\n')
            else:
                print('There\'s no available servers')

    def do_downloads_by_server(self, arg):
        """List the movies requested by servers and number of requests."""
        args = arg.split()
        if len(args) != 0:
            common.error('`downloads_by_server` doesn\'t'
                         'expect any arguments.')
        else:
            servers = self.central_server.download_service.get_servers()
            requests = self.central_server.client_service.get_requests()

            if not servers.is_empty():
                print("%i server(s):" % len(
                    servers.servers))
                print('')
                for server in servers.servers:
                    print('server:')
                    print(str(server))
                    print('downloads:')
                    server_requests = requests.get_requests_from_server(server)
                    if server_requests:
                        print(tabulate(
                            [request.to_row() for request
                             in server_requests],
                            headers=['Movie', 'Client'],
                            tablefmt="psql"))
                        print('')
                    else:
                        print('No downloads\n')
            else:
                print('There\'s no available servers')

    def do_clients_by_server(self, arg):
        """List the clients handled by each server"""

        args = arg.split()
        if len(args) != 0:
            common.error('`clients_by_server` doesn\'t expect any arguments.')
        else:
            servers = self.central_server.download_service.get_servers()

            if not servers.is_empty():
                print("%i server(s):" % len(
                    servers.servers))
                print('')
                for server in servers.servers:
                    print('server:')
                    print(str(server))
                    print('clients:')
                    if server.clients:
                        clients = [client[0] for client in server.clients]
                        print(tabulate(
                            [[c.username, c.host, str(c.port)] for c
                             in clients],
                            headers=['Username', 'Host', 'Port'],
                            tablefmt="psql"))
                        print('')
                    else:
                        print('No clients\n')
            else:
                print('There\'s no available servers')

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
        self.clients = ClientDict()
        self.movies = MovieDict()
        self.servers = ServerList()
        self.requests = RequestList()
        self.client_service = ClientService(self)
        self.download_service = DownloadServerService(self)
        self.shell = GggomCentralServerShell(self)

    def run(self):
        self.reactor.callInThread(self.shell.cmdloop)
        self.reactor.run()
