#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test Perlin
"""
import random

from pandac.PandaModules import PerlinNoise2
#from modules.world.map2d import Map_generator_2D
from PIL import Image

#gen = Map_generator_2D(iters = 3)
#for i, desc in gen.start():
    #pass

#map2d = gen.end_map

seed = 123

def test1():
    size = 256

    perlin = PerlinNoise2(size, size)
    perlin.setScale(20)

    start_x = 0
    start_y = 0

    image1 = Image.new("RGB", (size, size), (0, 0, 0, 0))
    image2 = Image.new("RGB", (size, size), (0, 0, 0, 0))
    image3 = Image.new("RGB", (size, size), (0, 0, 0, 0))
    image4 = Image.new("RGB", (size, size), (0, 0, 0, 0))
    main_image = Image.new("RGB", (size*2, size*2), (0, 0, 0, 0))
    cool_image = Image.new("RGB", (size*8, size*8), (0, 0, 0, 0))

    perlin_heights = {}
    for x in xrange(0, size):
        for y in xrange(0, size):
            color = int(round(perlin(x, y)*100)+100)
            perlin_heights[(x, y)] = color

    for x in xrange(0, size):
        for y in xrange(0, size):
            color = perlin_heights[(x, y)]
            #print x+(i*size), x+(j*size)
            image1.putpixel((x, y), (0 + color, 0 + color, 0+color))

    image2 = image1.copy()
    image3 = image1.copy()
    image4 = image1.copy()

    image2 = image2.transpose(Image.FLIP_LEFT_RIGHT)
    image3 = image3.transpose(Image.FLIP_TOP_BOTTOM)
    image4 = image3.transpose(Image.FLIP_LEFT_RIGHT)

    for x in xrange(size):
        for y in xrange(size):
            main_image.putpixel((x, y), image1.getpixel((x, y)))

    for x in xrange(size, size+size):
        for y in xrange(size):
            main_image.putpixel((x, y), image2.getpixel((x-size, y)))

    for x in xrange(size):
        for y in xrange(size, size+size):
            main_image.putpixel((x, y), image3.getpixel((x, y-size)))

    for x in xrange(size, size+size):
        for y in xrange(size, size+size):
            main_image.putpixel((x, y), image4.getpixel((x-size, y-size)))

    for x in xrange(0, size*8, size*2):
        for y in xrange(0, size*8, size*2):
            cool_image.paste(main_image, (x, y))


    cool_image.save('tiles.png', 'PNG')

def test2():
    size = 64

    perlin = PerlinNoise2(size, size, size, seed)

    image = Image.new("RGB", (size*6, size), (0, 0, 0, 0))
    perlin.setScale(20)
    for x in xrange(0, size):
        for y in xrange(0, size):
            color = int(round(perlin(x, y)*100)+100)
            image.putpixel((x, y), (0 + color, 0 + color, 0+color))

    perlin.setScale(15)
    for x in xrange(0, size):
        for y in xrange(0, size):
            color = int(round(perlin(x, y)*100)+100)
            image.putpixel((x+size, y), (0 + color, 0 + color, 0+color))

    perlin.setScale(10)
    for x in xrange(0, size):
        for y in xrange(0, size):
            color = int(round(perlin(x, y)*100)+100)
            image.putpixel((x+(size*2), y), (0 + color, 0 + color, 0+color))


    perlin.setScale(7)
    for x in xrange(0, size):
        for y in xrange(0, size):
            color = int(round(perlin(x, y)*100)+100)
            image.putpixel((x+(size*3), y), (0 + color, 0 + color, 0+color))

    perlin.setScale(5)
    for x in xrange(0, size):
        for y in xrange(0, size):
            color = int(round(perlin(x, y)*100)+100)
            image.putpixel((x+(size*4), y), (0 + color, 0 + color, 0+color))

    perlin.setScale(2)
    for x in xrange(0, size):
        for y in xrange(0, size):
            color = int(round(perlin(x, y)*100)+100)
            image.putpixel((x+(size*5), y), (0 + color, 0 + color, 0+color))

    image.save('octaves.png', 'PNG')

test1()
test2()
# get x = 3, y = 5  (+1 round)
# get x = 3, y = 5  (+1 round)

# vi: ft=python:tw=0:ts=4

