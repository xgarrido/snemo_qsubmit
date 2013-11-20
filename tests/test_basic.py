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
Some unit tests for BaseSetup
"""

import unittest
from qsubmit import BaseSetup


class BasicTest (unittest.TestCase):

    def test_1_parse (self):
        setup = BaseSetup (True)
        setup.parse ('./tests/dummy.conf')

    def test_1_submit (self):
        setup = BaseSetup (True)
        setup.parse ('./tests/dummy.conf')
        setup.submit ()
