#!/usr/bin/env python
from distutils.core import setup
import sys

if 'win' == sys.platform[:3]:
  import py2exe

setup(name='fabian',
  version='0.1',
  description='Image viewer for file series of diffraction images',
  license='GPL',
  maintainer='Henning Osholm Soerensen',
  maintainer_email='henning.sorensen@risoe.dk',
  url='http://fable.sourceforge.net',
  py_modules=['edfimage','tifimage','adscimage','brukerimage','bruker100image','marccdimage','pixel_trace'],
  scripts=["fabian.py"])

