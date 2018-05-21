"""
Lotus Lake
=====================

Python tools for analysing a collection of Lotus simulations (output files)
=====================
C.Losada de la Lastra
"""

from .__version__ import version
from .io import *
from .vis import *

def hello():
    # test function to confirm import has succeded
    print('hello from Lotus Lake version {0}'.format(version))
