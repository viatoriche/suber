#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test formules
"""

import math

def get_height(level, h):
    if h == 0:
        return 0
    high_level = abs(h)
    factor = 8
    mod = math.log(high_level, factor)
    return ((level+1) ** mod)**2 / h

x = 63
y = -1
if x>=0 and x<=63 and y>=0 and y<=63:
    print 'OK'
else:
    print 'NAY'

if __name__ == "__main__":
    print get_height(2, 5000)
# vi: ft=python:tw=0:ts=4

