#!/usr/bin/env python
# -*- coding: utf-8 -*-

# It script it publish under GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/licenses/gpl-3.0.en.html
# Author: the Galaxie Curses Team, all rights reserved

import unittest
from GLXCurses import Bin
from GLXCurses.libs.Utils import glxc_type


# Unittest
class TestBin(unittest.TestCase):
    def test_bin_type(self):
        self.assertTrue(glxc_type(Bin()))

    def test_bin_get_child(self):
        # create ou main Bin
        glxc_bin = Bin()
        # default value should be None
        self.assertEqual(glxc_bin.child, None)
        # create our child
        child = Bin()
        # Bin() is suppose to obtain a .add() method from Container() Class
        glxc_bin.add(child)
        # test get_child
        self.assertEqual(glxc_bin.child.widget, child)
