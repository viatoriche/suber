#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Global config
"""

class Config():
    """Static parameters for voxplanet

    size_mod - degree for size of world -- 2 ** size_mod

    size_region - size of region for fix of round float type on big location

    root_level - first level // deprecated, but need for classes

    chunk_len - count of voxels in chunk - example: chunk_len = 4 --> 4x4

    count_chunks - count of chunk for divide quadro_node -- need for LOD

    factor_far - factor for LOD, size of minimal chunk * factor_far -> distance for LOD

    min_far - minimum distance for LOD

    land/low/mid/high_mount_level - heights for squares in meters

    factor_land/low/mid/high_level - chance factor for generate heights

    iters - count of iteration for generator of planet, more - high quality

    min_land - minimum % of lands
    max_land - maximum % of lands

    min_continents - min counts of start points for continents generate
    max_continents - max counts of start points for continents generate
    """
    #size_world = 16777216
    size_mod = 24
    size_world = 2**size_mod

    size_region = size_world / 256
    #size_region = size_world

    # detalized
    min_level = 2
    tree_level = min_level+5
    chunk_len = 2 ** min_level
    count_chunks = 4
    count_levels = 2
    chunk_delay = 0.01
    tree_far = 200
    tree_billboard = 2

    land_mount_level = 1, 200
    low_mount_level = 201, 1000
    mid_mount_level = 1001, 3000
    high_mount_level = 3001, 10000

    factor_high_mount = 30
    factor_mid_mount = 40
    factor_low_mount = 60
    factor_land_mount = 100

    # for Map_generator_2D
    iters = 5
    # %
    min_land = 35
    max_land = 55
    # start points of continents
    min_continents = 4
    max_continents = 6

    tree_models = 30
    add_pre_heights = True
# vi: ft=python:tw=0:ts=4

