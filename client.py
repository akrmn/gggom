#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GGGOM Geodistributed Getter Of Movies Client."""

from __future__ import print_function
from cmd import Cmd
from sys import stderr
from twisted.internet import reactor


class GggomClientShell(Cmd):
    """GGGOM Client Shell."""

    intro = (
        'Welcome to the gggom shell.\n'
        'Type help or ? to list commands.\n')
    prompt = 'gggom> '
    username = None

    # Commands
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

    # Helper methods
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

    def cmdloop_with_interrupt(self):
        """Shell loop.

        Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument, while catching
        KeyboardInterrupts.

        """
        print(self.intro)
        try:
            self.cmdloop(intro="")
        except KeyboardInterrupt:
            print("^C")
            return True

    def _leave(self, arg):
        print('Thank you for using GGGOM.')
        return True

    def _must_register(self):
        self._error("You must `register` before issuing this command.")
        return

    def _error(self, text):
        print("ERROR:", text, file=stderr)


if __name__ == '__main__':
    reactor.callInThread(GggomClientShell().cmdloop_with_interrupt)
    reactor.run()
