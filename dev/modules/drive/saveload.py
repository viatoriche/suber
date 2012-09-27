#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)

Save and load all World
"""

from config import Config

class SaveMap():
    """Class for saving world

    """
    config = Config()
    def __init__(self, map3d):
        self.map3d = map3d

# vi: ft=python:tw=0:ts=4

