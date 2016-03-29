# -*- coding: utf-8 -*-

from __future__ import print_function
from sys import stderr, stdout
from threading import Thread, RLock, Condition

def error(text):
    print("ERROR:", text, file=stderr)

class _Spinner(Thread):
    def __init__(self, message):
        Thread.__init__(self)
        self.rlock = RLock()
        self.cv = Condition()
        self.__chars = u"⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        if len(message) > 0:
            self.__message = " " + message
        else:
            self.__message = ""
        self.__message_length = len(self.__message)

    def __clear(self):
        stdout.write(
            '\b' * (self.__message_length + 2) +
            ' '  * (self.__message_length + 2) +
            '\b' * (self.__message_length + 2))
        stdout.flush()

    def __call__(self):
        self.start()

    def start(self):
        self.stopFlag = 0
        Thread.start(self)

    def stop(self):
        """To be called by the 'main' thread: Will block and wait for the
        thread to stop before returning control to 'main'."""

        self.stopFlag = 1

        # Wake up ahead of time if needed
        self.cv.acquire()
        self.cv.notify()
        self.cv.release()

        # Block and wait here untill thread fully exits its run method.
        self.rlock.acquire()

    def run(self):
        self.rlock.acquire()
        self.cv.acquire()
        stdout.write('  ' + self.__message)
        stdout.write('\b' * self.__message_length)
        stdout.flush()
        while 1:
            for char in self.__chars:
                self.cv.wait(0.1)
                if self.stopFlag:
                    self.__clear()
                    try :
                        return
                    finally :
                        # release lock immediatley after returning
                        self.rlock.release()
                stdout.write('\b')
                stdout.write(char)
                stdout.flush()

class Spinner():
    def __init__(self):
        self.__current = None

    def start(self, message = ""):
        self.__current = _Spinner(message)
        self.__current.start()

    def stop(self):
        if self.__current is not None:
            self.__current.stop()
