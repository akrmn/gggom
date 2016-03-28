#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Client."""

from __future__ import print_function
import signal
from cmd import Cmd
from sys import stdin, stdout, stderr
from optparse import OptionParser
from twisted.internet import reactor
from tabulate import tabulate

from central_server_service import ClientService, DownloadServerService
from movie import Movie, MovieList, Client, Server


class GggomCentralServerShell(Cmd):
    """GGGOM Central Server Shell."""

    intro = (
        'Welcome to the gggom shell.\n'
        'Type help or ? to list commands.\n'
        'To leave, use exit or ^D.\n')
    prompt = 'gggom> '

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
            _error('`movies_by_server` doesn\'t expect any arguments.')

        else:
            def print_movies_by_server(movies, servers):
                if not servers.is_empty():
                    print("%i available server(s):" % len(servers.get_server_list()))
                    print('')
                    for server in servers.get_server_list():
                        print('server:')
                        print(server.to_string())
                        print('movies:')
                        if not movies.is_empty():
                            print(tabulate(
                                [movie.to_row() for movie in movies.get_movie_dict() if server == movies.get_servers(movie)],
                                headers=['Id', 'Title', 'Size'], tablefmt="psql"))
                            print('')
                        else: print('No movies\n')
                else:
                    print('There\'s no available servers')

            movies, servers = self.server_service.movies_by_server()
            print_movies_by_server(movies, servers)

    def do_downloads_by_server(self, arg):
        """List the movies requested by servers and how many times they were requested."""
        args = arg.split()
        if len(args) != 0:
            _error('`downloads_by_server` doesn\'t expect any arguments.')
        else:
            print('server 1: fakemovie requested 23 times')

    def do_clients_by_server(self, arg):
        """List the clients handled by each server"""

        args = arg.split()
        if len(args) != 0:
            _error('`clients_by_server` doesn\'t expect any arguments.')
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

    def _must_register(self):
        _error("You must `register` before issuing this command.")
        return


def _error(text):
    print("ERROR:", text, file=stderr)


def parse_args():
    usage = ("%prog [options]...\n\n"
             "This is the central server program.\n"
             "If no port is given for the server, 26 is used.\n"
             "If no port is given for the client, 40 is used.")

    parser = OptionParser(usage)

    help = "The port to listen on for servers. Default is 26."
    parser.add_option('--server-port', type='int', help=help, dest="server_port")

    help = "The port to listen on for clients. Default is 40."
    parser.add_option('--client-port', type='int', help=help, dest="client_port")

    options, args = parser.parse_args()

    if len(args) != 0:
        parser.error("No arguments are expected")

    def parse_port(port):
        if not port.isdigit():
            parser.error('Ports must be integers.')

        return int(port)

    if (options.client_port is not None):
        client_port = parse_port(options.client_port)
    if (options.server_port is not None):
        server_port = parse_port(options.server_port)

    return options


def main():
    options = parse_args()

    signal.signal(signal.SIGINT, signal.SIG_IGN)

    client_service = ClientService(reactor, options.client_port or 40)
    server_service = DownloadServerService(reactor, options.server_port or 26)
    shell = GggomCentralServerShell(client_service, server_service)

    reactor.callInThread(shell.cmdloop)
    reactor.run()


if __name__ == '__main__':
    main()
