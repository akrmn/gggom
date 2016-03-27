#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Client."""

from __future__ import print_function
import signal
from cmd import Cmd
from sys import stdin, stdout, stderr
from twisted.internet import threads, reactor, defer
from twisted.web.client import getPage
from twisted.web.error import Error


class GggomClientShell(Cmd):
    """GGGOM Client Shell."""

    intro = (
        'Welcome to the gggom shell.\n'
        'Type help or ? to list commands.\n'
        'To leave, use exit or ^D.\n')
    prompt = 'gggom> '
    username = None

    # ======================================================================= #
    # Commands                                                                #
    # ======================================================================= #
    def do_register(self, arg):
        """Register the user with the specified username."""
        args = arg.split()
        if len(args) != 1:
            self._error("`register` takes a single argument")
        else:
            print('Registering as user %s' % args[0])
            self.username = args[0]

    def do_list_movies(self, arg):
        """Fetch the list of available movies from the Central Server."""
        if self.username is None:
            return self._must_register()

        args = arg.split()
        if len(args) == 0:
            print('Fetching movie list from the Central Server.')
        elif len(args) != 0:
            self._error('`list_movies` doesn\'t expect any arguments.')

    def do_download(self, arg):
        """Begin downloading the specified movie."""
        if self.username is None:
            return self._must_register()

        args = arg.split()
        if len(args) == 0:
            self._error('`download` expects one argument.')
        else:  # I think it could work for many movies at the same time
            for movie in args:
                print('Downloading %s' % movie)

    def do_status(self, arg):
        """Show the status of the specified movie."""
        if self.username is None:
            return self._must_register()

        args = arg.split()
        if len(args) == 0:
            self._error('`status` expects one argument.')
        else:  # I think it could work for many movies at the same time
            for movie in args:
                print('The status of %s is ok.' % movie)

    def do_exit(self, arg):
        """Stop downloads and exit."""
        return self._leave(arg)

    def do_EOF(self, arg):
        """Stop downloads and exit."""
        print("^D")
        return self._leave(arg)

    # def inThread(self):
    #     try:
    #         result = threads.blockingCallFromThread(
    #             reactor, getPage, "http://google.com/")
    #     except Error, exc:
    #         print(exc)
    #     else:
    #         print(result)
    #
    # def do_try(self, arg):
    #     reactor.callInThread(self.inThread)

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
        self._error("You must `register` before issuing this command.")
        return

    def _error(self, text):
        print("ERROR:", text, file=stderr)


def main():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    shell = GggomClientShell()

    reactor.callInThread(shell.cmdloop)
    reactor.run()


if __name__ == '__main__':
    main()
