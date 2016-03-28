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

from download_server_service import ClientService, CentralServerService
from movie import Movie, MovieList, Client, Server


class GggomDownloadServerShell(Cmd):
    """GGGOM Download Server Shell."""

    intro = (
        'Welcome to the gggom shell.\n'
        'Type help or ? to list commands.\n'
        'To leave, use exit or ^D.\n')
    prompt = 'gggom> '
    movies = []

    def __init__(self, client_service, server_service):
        Cmd.__init__(self)
        self.client_service = client_service
        self.server_service = server_service
        self.movies.append(Movie('fakeone', "Harry Potter and the Fakey Fake", 35))
        self.movies.append(Movie('phoney', "Draco Malfoy and the Dark Lord", 35))
        def callback(result):
            print('Registered successfully')

        def errback(reason):
            _error(reason.getErrorMessage())

        self.server_service.register(self.movies, callback, errback)
        self.client_service.add_movie_list(self.movies)


    # ======================================================================= #
    # Commands                                                                #
    # ======================================================================= #
    def do_view_downloads(self, arg):
        """List the current downloads."""
        args = arg.split()

        if len(args) != 0:
            _error('`view_downloads` doesn\'t expect any arguments.')

        else:
            print('9 downloads: (...)')

    def do_downloaded_movies(self, arg):
        """List what movies have been downloaded and how many times."""
        args = arg.split()
        if len(args) != 0:
            _error('`downloaded_movies` doesn\'t expect any arguments.')
        else:
            print('fakemovie downloads: 15')

    def do_list_clients(self, arg):
        """List the clients that download movies from the server."""

        args = arg.split()
        if len(args) != 0:
            _error('`list_clients` doesn\'t expect any arguments.')
        else:
            print('client 1: best_client, 192.168.2.1')

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
    usage = ("%prog [options] server_ip[:port]...\n\n"
             "This is the download server program.\n"
             "If no port is given for the server, 26 is used.\n"
             "If no port is given as an option to listen to clients, 16 is used.")

    parser = OptionParser(usage)

    help = "The port to listen on. Default is 16."
    parser.add_option('--port', type='int', help=help)

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Provide exactly one server address.')

    def parse_address(arg):
        if ':' not in arg:
            host = arg
            port = '26'
        else:
            host, port = arg.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    host, port = parse_address(args[0])

    return host, port, options


def main():
    server_host, server_port, options = parse_args()

    signal.signal(signal.SIGINT, signal.SIG_IGN)

    client_service = ClientService(reactor, options.port or 16)
    server_service = CentralServerService(reactor, server_host, server_port, options.port or 16)
    shell = GggomDownloadServerShell(client_service, server_service)

    reactor.callInThread(shell.cmdloop)
    reactor.run()


if __name__ == '__main__':
    main()
