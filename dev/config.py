#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Global config
"""

class Config():
    size_world = 16777216
    factor = 8
    factor_double = 64
    factor_tor = 7
    factor_double_tor = 63
    cube_meter = 1
    land_level = 24
    root_level = 0
    count_chanks = 6
    # one cube = 2 cube
    factor_down = 2
    factor_down_tor = 1
    # 0x63 = 0x31 + 32x63
    factor_down_size = 32

    size_chank = 8
    cube_size = 1

    default_height_level = 1

    # height cubes
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

    name_game = 'Suber'

# vi: ft=python:tw=0:ts=4

