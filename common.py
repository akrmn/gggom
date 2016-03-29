# -*- coding: utf-8 -*-

from __future__ import print_function
from sys import stderr

def error(text):
    print("ERROR:", text, file=stderr)
