#!/usr/bin/env python
# -*- coding: latin-1 -*-
"""
PyCSP.greenlets implementation of the CSP Core functionality (Channels, Processes, PAR, ALT).

Copyright (c) 2009 John Markus Bjørndalen <jmb@cs.uit.no>,
      Brian Vinter <vinter@diku.dk>, Rune M. Friborg <runef@diku.dk>
See LICENSE.txt for licensing details (MIT License). 
"""

# Test for Greenlets
import sys
try: from greenlet import greenlet
except ImportError, e:
    try: from py.magic import greenlet
    except ImportError, e: 
        sys.stderr.write("PyCSP.greenlets requires the greenlet module, recommended version is 0.2 and is\navailable from http://pypi.python.org/pypi/greenlet/.\n\n")
        raise ImportError(e)

#from pycsp.greenlets import *
# Imports
#from pycsp.greenlets.scheduling import io
from pycsp.greenlets.guard import Skip
from guard import Timeout
from pycsp.greenlets.alternation import choice
from alternation import Alternation
from pycsp.greenlets.channel import ChannelPoisonException, ChannelRetireException
from channel import Channel
from pycsp.greenlets.channelend import retire, poison, IN, OUT
from process import process, Process, Parallel, Spawn
from pycsp.greenlets.process import Sequence
from simulation import Simulation, Io, io, Now

from showtree import *
version = (0,6,2, 'simulation')

def test_suite():
    import unittest
    import doctest
    import simulation, guard, alternation, channel, process

    suite = unittest.TestSuite()
    for mod in simulation, guard, alternation, channel, process:
        suite.addTest(doctest.DocTestSuite(mod))
    suite.addTest(doctest.DocTestSuite())
    return suite

# Run tests
if __name__ == '__main__':
    import unittest

    suite = test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
