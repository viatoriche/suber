#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test square random
"""
# 4x4 , size - 4
#self = [# 0  1  2  3
#         [0, 0, 0, 0], # 0
#         [0, 0, 0, 0], # 1
#         [0, 0, 0, 0], # 2
#         [0, 0, 0, 0]  # 3
#        ]

# answer:
# 00, 11
# 20, 31
# 02, 13
# 22, 33

import random

self = {}
size = 16
for x in xrange(0,size):
    for y in xrange(0,size):
        self[(x, y)] = 0


def diamond_it(sx, sy, size):
    #print sx, sy, sx+size-1, sy+size-1, size
    dsize = size/2
    if dsize <= 0:
        return
    ex = sx+size-1
    ey = sy+size-1
    print sx,':', sy, '  +',size

    # lets get math style
    RAND = random.randint

    A = sx, sy
    B = ex, sy
    C = sx, ey
    D = ex, ey
    E = sx+dsize, sy+dsize
    F = sx, sy + dsize
    G = sx + dsize, sy
    H = ex, sy + dsize
    I = sx + dsize, ey


    d = -2, 2


    self[E] = (self[A] + self[B] + self[C] + self[D]) / 4 + RAND(*d)

    self[F] = (self[A] + self[C] + self[E] + self[E]) / 4 + RAND(*d)
    self[G] = (self[A] + self[B] + self[E] + self[E]) / 4 + RAND(*d)
    self[H] = (self[B] + self[D] + self[E] + self[E]) / 4 + RAND(*d)
    self[I] = (self[C] + self[D] + self[E] + self[E]) / 4 + RAND(*d)

    diamond_it(A[0], A[1], dsize)
    diamond_it(G[0], G[1], dsize)
    diamond_it(F[0], F[1], dsize)
    diamond_it(E[0], E[1], dsize)

diamond_it(0, 0, size)
s = ''
for x in xrange(0, size):
    s += '\n\n'
    for y in xrange(0, size):
        a = self[(x, y)]
        if a <0:
            s += '{0} | '.format(self[(x, y)])
        else:
            s += ' {0} | '.format(self[(x, y)])

print s
# vi: ft=python:tw=0:ts=4

