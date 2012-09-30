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
size = 256

perlin = PerlinNoise2(size, size)
# level 1
perlin.setScale(20)

#start_x = random.randint(0, size-1024)
#start_y = random.randint(0, size-768)
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


cool_image.save('heightmap.png', 'PNG')
# get x = 3, y = 5  (+1 round)

# vi: ft=python:tw=0:ts=4

