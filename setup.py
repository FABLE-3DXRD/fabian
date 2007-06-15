#!/usr/bin/env python
from distutils.core import setup,Extension
import sys

mar345_backend=Extension('mar345_io',sources = ['src/mar345_iomodule.c','src/ccp4_pack.c'])

setup(name='fabian',
  version='0.2',
  description='Image viewer for file series of diffraction images',
  license='GPL', maintainer='Henning Osholm Soerensen and Erik Knudsen',
  maintainer_email='henning.sorensen@risoe.dk or erik.knudsen@risoe.dk',
  url='http://fable.sourceforge.net',
  py_modules=['edfimage','tifimage','adscimage','brukerimage','bruker100image',
  'marccdimage','mar345image','pnmimage','pixel_trace','rocker','image_file_series'],
  ext_modules=[mar345_backend],
  scripts=["fabian.py"])

