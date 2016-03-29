# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Download Server."""

from __future__ import print_function
import signal
from cmd import Cmd
from optparse import OptionParser
from twisted.internet import reactor
from tabulate import tabulate

from download_server_service import ClientService, CentralServerService
from movie import Movie
import common


class GggomDownloadServerShell(Cmd):
    """GGGOM Download Server Shell."""

    intro = (
        'Welcome to the gggom Download Server shell.\n'
        'Type help or ? to list commands.\n'
        'To leave, use exit or ^D.\n')
    prompt = 'Gggom$ '
    movies = []

    def __init__(self, client_service, server_service):
        Cmd.__init__(self)
        self.client_service = client_service
        self.server_service = server_service

    # ======================================================================= #
    # Commands                                                                #
    # ======================================================================= #
    def do_view_downloads(self, arg):
        """List the current downloads."""
        args = arg.split()

        if len(args) != 0:
            common.error('`view_downloads` doesn\'t expect any arguments.')

        else:
            print('9 downloads: (...)')

    def do_downloaded_movies(self, arg):
        """List what movies have been downloaded and how many times."""
        args = arg.split()
        if len(args) != 0:
            common.error('`downloaded_movies` doesn\'t expect any arguments.')
        else:
            print('fakemovie downloads: 15')

    def do_list_clients(self, arg):
        """List the clients that download movies from the server."""

        args = arg.split()
        if len(args) != 0:
            common.error('`list_clients` doesn\'t expect any arguments.')
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

class DownloadServer:
    def __init__(self, host, port, client_port, options):
        self.host = host
        self.port = port
        self.client_port = client_port
        self.options = options
        self.reactor = reactor
        self.client_service = ClientService(self.reactor, client_port)
        self.server_service = CentralServerService(self.reactor, host, port,
                                                   client_port)
        self.shell = GggomDownloadServerShell(self.client_service,
                                              self.server_service)
        self.movies = []
        self.spinner = common.Spinner()

    def onStart(self):
        def callback(result):
            self.spinner.stop()
            self.shell.cmdloop()

        def errback(reason):
            self.spinner.stop()
            common.error(reason.getErrorMessage())
            reactor.callFromThread(self.reactor.stop)

        self.movies.append(Movie('fakeone',
                                 "Harry Potter and the Fakey Fake", 35))
        self.movies.append(Movie('phoney',
                                 "Draco Malfoy and the Dark Lord", 35))

        self.spinner.start("Registering at %s:%i" % (self.host, self.port))

        self.server_service.register(self.movies, callback, errback)

    def run(self):
        self.reactor.callInThread(self.onStart)
        self.reactor.run()
