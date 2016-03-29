# -*- coding: utf-8 -*-

from __future__ import print_function
from sys import stderr, stdout
from threading import Thread, RLock, Condition

def error(text):
    print("ERROR:", text, file=stderr)

class Spinner(Thread):
    def __init__(self, speed=0.1):
        Thread.__init__(self)
        self.rlock = RLock()
        self.cv = Condition()
        self.__chars = u"⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.__message = ""
        self.__message_length = 0

    def __clear(self):
        stdout.write(
            '\b' * (self.__message_length + 2) +
            ' '  * (self.__message_length + 2) +
            '\b' * (self.__message_length + 2))
        stdout.flush()

    def __call__(self):
        self.start()

    def start(self, message=""):
        self.stopFlag = 0
        if len(message) > 0:
            self.__message = " " + message
        else:
            self.__message = ""
        self.__message_length = len(self.__message)
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
