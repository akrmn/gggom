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

from central_server_service import ClientService
from movie import Movie, MovieList, Client, Server


class GggomClientShell(Cmd):
    """GGGOM Client Shell."""

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
            print('1 available server(s)')
            #def callback(result):
            #    print("%i available server(s):" % len(result))

            #    print(tabulate(
            #        [movie.to_row() for movie in result],
            #        headers=['Id', 'Title', 'Size'], tablefmt="psql"))

            #def errback(reason):
            #    _error(reason.getErrorMessage())

            #self.service.list_movies(callback, errback)

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
    usage = ("%prog [options] server_ip[:port] client_ip[:port]...\n\n"
             "This is the central server program.\n"
             "If no port is given for the server, 26 is used."
             "If no port is given for the client, 40 is used.")

    parser = OptionParser(usage)

    options, args = parser.parse_args()

    if len(args) != 2:
        parser.error('Provide one server address and one client address.')

    def parse_address(arg, flag):
        if ':' not in arg:
            host = arg
            if flag == 'client':
                port = '40'
            else:
                port = '26'
        else:
            host, port = arg.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    server_host, server_port = parse_address(args[0], 'server')
    client_host, client_port = parse_address(args[1], 'client')

    return server_host, server_port, client_host, client_port, options


def main():
    server_port, server_host, client_host, client_port, options = parse_args()

    signal.signal(signal.SIGINT, signal.SIG_IGN)

    client_service = ClientService(reactor, client_host, client_port)
    server_service = None #ServerService(reactor, server_host, server_port)
    shell = GggomClientShell(client_service, server_service)

    reactor.callInThread(shell.cmdloop)
    reactor.run()


if __name__ == '__main__':
    main()
