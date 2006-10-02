#!/usr/bin/env python
from distutils.core import setup
import sys

if 'win' == sys.platform[:3]:
  import py2exe

setup(name='ImAM',
  version='0.1',
  description='Image viewer for edf-image file series',
  license='GPL',
  maintainer='Henning Osholm Soerensen',
  maintainer_email='osho@risoe.dk',
  url='http://fable.sourceforge.net',
  py_modules=['edfimage'],
  scripts=["ImAM.py"])

