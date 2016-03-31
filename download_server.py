# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Download Server."""

from __future__ import print_function
import signal, os
from cmd import Cmd
from optparse import OptionParser
from twisted.internet import reactor
from tabulate import tabulate

import xml.etree.cElementTree as ET

from download_server_service import ClientService, CentralServerService
from movie import Movie
from client_item import ClientItem
import common


class GggomDownloadServerShell(Cmd):
    """GGGOM Download Server Shell."""

    intro = (
        'Welcome to the gggom Download Server shell.\n'
        'Type help or ? to list commands.\n'
        'To leave, use exit or ^D.\n')
    prompt = 'Gggom$ '

    def __init__(self, download_server):
        Cmd.__init__(self)
        self.download_server = download_server

    # ======================================================================= #
    # Commands                                                                #
    # ======================================================================= #
    def do_current_downloads(self, arg):
        """List the current downloads."""
        args = arg.split()

        if len(args) != 0:
            common.error('`current_downloads` doesn\'t expect any arguments.')
        else:
            if self.download_server.current_downloads:
                print("Current downloads:")

                rows = [[movie.title, transfers] for (movie, transfers)
                        in self.download_server.current_downloads.items()]

                print(tabulate(rows, headers=['Movie', 'Ongoing downloads'],
                               tablefmt="psql"))
            else:
                print("No movies are being downloaded")

    def do_downloaded_movies(self, arg):
        """List what movies have been downloaded and how many times."""
        args = arg.split()
        if len(args) != 0:
            common.error('`downloaded_movies` doesn\'t expect any arguments.')
        else:
            if self.download_server.finished_downloads:
                print("Downloaded movies:")

                rows = [[movie.title, downloads] for (movie, downloads)
                        in self.download_server.finished_downloads.items()]

                print(tabulate(rows, headers=['Movie', 'Finished downloads'],
                               tablefmt="psql"))
            else:
                print("No movies have been downloaded")

    def do_loyal_clients(self, arg):
        """List the clients that download movies from the server."""

        args = arg.split()
        if len(args) != 0:
            common.error('`loyal_clients` doesn\'t expect any arguments.')
        else:
            if self.download_server.loyal_clients:
                print("Loyal clients:")

                rows = [[client.username, client.host, downloads]
                        for (client, downloads)
                        in self.download_server.loyal_clients.items()]

                rows.sort(key = lambda x: [-x[2], x[0]])

                print(tabulate(rows,
                               headers=['Client username','host','Downloads'],
                               tablefmt="psql"))
            else:
                print("No clients have downloaded movies yet")

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
        self.movies = []
        self.current_downloads = {}
        self.finished_downloads = {}
        self.loyal_clients = {}
        self.client_service = ClientService(self)  
        self.server_service = CentralServerService(self)
        self.shell = GggomDownloadServerShell(self)
        self.spinner = common.Spinner()

    def load_movies(self):
        # FIXME: This should ALL be loaded from an XML file
        tree = ET.parse('ds_metadata.xml')
        root = tree.getroot()
        my_movies = root.find('movies')
        n = 1
        for movie in my_movies:
        	path = movie.attrib['path']
        	total_size = os.path.getsize(path)
        	size = total_size / 1024
        	if size == 0 or total_size%1024 != 0:
        		size+=1
        	new_movie = Movie(movie.attrib['id'],movie.text,size,path)
        	self.finished_downloads[new_movie] = n
        	self.movies.append(new_movie)
        	n+=1

        gaby = ClientItem("gaby", "192.168.0.5", "5412")
        gustavo_e = ClientItem("gustavo_e", "192.168.0.8", "5712")
        gustavo_g = ClientItem("gustavo_g", "192.168.0.10", "5852")
        oscar = ClientItem("oscar", "192.168.0.55", "5440")
        moises = ClientItem("moises", "192.168.0.140", "4522")

        self.loyal_clients[gaby] = 7
        self.loyal_clients[gustavo_e] = 5
        self.loyal_clients[gustavo_g] = 6
        self.loyal_clients[oscar] = 2
        self.loyal_clients[moises] = 6

    def onStart(self):
        def callback(result):
            self.spinner.stop()
            self.shell.cmdloop()

        def errback(reason):
            self.spinner.stop()
            common.error(reason.getErrorMessage())
            reactor.callFromThread(self.reactor.stop)

        self.load_movies()

        self.spinner.start("Registering at %s:%i" % (self.host, self.port))

        self.server_service.register(callback, errback)

    def run(self):
        self.reactor.callInThread(self.onStart)
        self.reactor.run()
