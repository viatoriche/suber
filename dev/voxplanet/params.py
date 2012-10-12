#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""All parameters for world

Author:  Viator <viator@via-net.org>
License: GPL (see http://www.gnu.org/licenses/gpl.txt)
"""

class Params(dict):
    """All dynamic parameters here

    ['name'] = value

    function status(text)
    root_node - NodePath
    chunks_tex - texmap for chunks
    function tex_uv_height - input(height), return - uv coords
    sun - plight
    fog - fog
    """
    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise 'name not found'

if __name__ == "__main__":
    p = Params()
    p.test = 'lol'
    print p['test']
    p['jopa'] = 'nya'
    print p.jopa

# vi: ft=python:tw=0:ts=4

