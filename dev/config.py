#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Global config
"""

class Config():
    factor = 8
    factor_double = 64
    factor_tor = 7
    factor_double_tor = 63
    cube_meter = 1
    land_level = 8
    root_level = 0
    count_chanks = 6
    factor_down = 2

    default_height_level = 1

    # height cubes
    land_mount_level = 1, 200
    low_mount_level = 200, 1000
    mid_mount_level = 1000, 3000
    high_mount_level = 3000, 10000

    # 5%
    factor_high_mount = 5
    # 10%
    factor_mid_mount = 15
    # 30%
    factor_low_mount = 45
    # 55%
    factor_land_mount = 100

    name_game = 'Suber'

# vi: ft=python:tw=0:ts=4

