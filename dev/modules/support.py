#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
support Classes and functions for drive
"""

from direct.stdpy import threading2 as panda_threading
import threading

def generate_hash(dic = {}):
    """
    docstring for generate_hash
    """
    ghash = hashlib.md5(random.random()).hexdigest()
    while dic.has_key(ghash):
        ghash = hashlib.md5(random.random()).hexdigest()
    return ghash

class ThreadPandaDo(panda_threading.Thread):
    """
    docstring for ThreadPandaDo
    """
    def __init__(self, doit, *args, **params):
        """
        doit - callable object, and next parameters for him
        """
        panda_threading.Thread.__init__(self)
        self.doit = doit
        self.result = None
        self.done = False
        self.args = args
        self.params = params

    def run(self):
        self.result = self.doit(*self.args, **self.params)
        self.done = True

class ThreadDo(threading.Thread):
    """
    docstring for ThreadDo
    """
    def __init__(self, doit, *args, **params):
        """
        doit - callable object, and next parameters for him
        """
        threading.Thread.__init__(self)
        self.doit = doit
        self.result = None
        self.done = False
        self.args = args
        self.params = params

    def run(self):
        self.result = self.doit(*self.args, **self.params)
        self.done = True

if __name__ == "__main__":
    print get_size_world()
# vi: ft=python:tw=0:ts=4

