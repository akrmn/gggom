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

from client_service import ClientService
from movie import Movie, MovieList, Client, Server


class GggomClientShell(Cmd):
    """GGGOM Client Shell."""

    intro = (
        'Welcome to the gggom shell.\n'
        'Type help or ? to list commands.\n'
        'To leave, use exit or ^D.\n')
    prompt = 'gggom> '
    username = None

    def __init__(self, service):
        Cmd.__init__(self)
        self.service = service

    # ======================================================================= #
    # Commands                                                                #
    # ======================================================================= #
    def do_register(self, arg):
        """Register the user with the specified username."""
        args = arg.split()

        if len(args) != 1:
            _error("`register` takes a single argument")

        else:
            username = args[0]

            def callback(result):
                print('Registered successfully')
                self.username = username

            def errback(reason):
                _error(reason.getErrorMessage())

            self.service.register(username, callback, errback)

    def do_list_movies(self, arg):
        """Fetch the list of available movies from the Central Server."""
        args = arg.split()

        if len(args) != 0:
            _error('`list_movies` doesn\'t expect any arguments.')

        else:
            def callback(result):
                print("%i available movie(s):" % len(result))

                print(tabulate(
                    [movie.to_row() for movie in result],
                    headers=['Id', 'Title', 'Size'], tablefmt="psql"))

            def errback(reason):
                _error(reason.getErrorMessage())

            self.service.list_movies(callback, errback)

    def do_download(self, arg):
        """Begin downloading the specified movie."""
        if self.username is None:
            return self._must_register()

        args = arg.split()
        if len(args) == 0:
            _error('`download` expects one argument.')
        else:  # I think it could work for many movies at the same time
            for movie in args:
                print('Downloading %s' % movie)
                print('/stub/')

    def do_status(self, arg):
        """Show the status of the specified movie."""
        if self.username is None:
            return self._must_register()

        args = arg.split()
        if len(args) == 0:
            _error('`status` expects one argument.')
        else:  # I think it could work for many movies at the same time
            for movie in args:
                print('The status of %s is ok.' % movie)
                print('/stub/')

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
             "This is the client program.\n"
             "If no port is given for the server, 40 is used.")

    parser = OptionParser(usage)

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Provide exactly one server address.')

    def parse_address(arg):
        if ':' not in arg:
            host = arg
            port = '40'
        else:
            host, port = arg.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    host, port = parse_address(args[0])

    return host, port, options


def main():
    host, port, options = parse_args()

    signal.signal(signal.SIGINT, signal.SIG_IGN)

    service = ClientService(reactor, host, port)
    shell = GggomClientShell(service)

    reactor.callInThread(shell.cmdloop)
    reactor.run()


if __name__ == '__main__':
    main()
