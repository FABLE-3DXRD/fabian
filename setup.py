#!/usr/bin/env python
from distutils.core import setup
import sys

setup(name='fabian',
  version='0.2',
  description='Image viewer for file series of diffraction images',
  license='GPL', maintainer='Henning Osholm Soerensen and Erik Knudsen',
  maintainer_email='henning.sorensen@risoe.dk or erik.knudsen@risoe.dk',
  url='http://fable.sourceforge.net',
  py_modules=['edfimage','tifimage','adscimage','brukerimage','bruker100image',
  'marccdimage','pnmimage','pixel_trace','rocker','image_file_series'],
  scripts=["fabian.py"])

