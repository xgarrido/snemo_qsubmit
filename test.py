#!/usr/bin/env python

# Copyright (C) 2012-2013  Xavier Garrido <garrido@lal.in2p3.fr>
#
# This file is part of qsubmit.
#
# Qsubmit is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distrubuted in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

"""
Do the unit tests!
"""

import os
import re
import sys
import unittest

sys.path.append ('tests')

from test_basic import BasicTest

def main ():

    suite = unittest.TestSuite ()
    suite.addTest (unittest.makeSuite (BasicTest))
    runner = unittest.TextTestRunner (verbosity=2)
    result = runner.run (suite)

if __name__ == '__main__':
    main ()

# end of test.py
