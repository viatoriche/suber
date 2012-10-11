#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Global config
"""

class Config():
    #size_world = 16777216
    size_mod = 24
    size_world = 2**size_mod

    size_region = size_world / 256
    root_level = 0

    # detalized /2
    chunk_len = 16
    factor_far = 25
    min_far = 1000

    land_mount_level = 1, 200
    low_mount_level = 201, 1000
    mid_mount_level = 1001, 3000
    high_mount_level = 3001, 10000

    # 5%
    factor_high_mount = 30
    # 10%
    factor_mid_mount = 40
    # 35%
    factor_low_mount = 60
    # 50%
    factor_land_mount = 100

    # for Map_generator_2D
    iters = 5
    # %
    min_land = 35
    max_land = 55
    # start points of continents
    min_continents = 4
    max_continents = 6

    tree_models = 10
# vi: ft=python:tw=0:ts=4

