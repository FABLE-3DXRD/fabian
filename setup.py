#!/usr/bin/env python
from distutils.core import setup,Extension
import sys

mar345_backend=Extension('mar345_io',sources = ['src/mar345_iomodule.c','src/ccp4_pack.c'])

setup(
  name='fabian',
  version='RELEASE',
  description='Image viewer for file series of diffraction images',
  license='GPL', maintainer='Henning Osholm Soerensen and Erik Knudsen',
  maintainer_email='henning.sorensen@risoe.dk or erik.knudsen@risoe.dk',
  url='http://fable.sourceforge.net',
  packages=['Fabian'],
  #py_modules=['edfimage','tifimage','adscimage','brukerimage','bruker100image',
  #'marccdimage','mar345image','pnmimage','pixel_trace','rocker','image_file_series','insert_peaks'],
  ext_modules=[mar345_backend],
  package_dir={"Fabian": "src"},
  scripts=["scripts/fabian.py", "scripts/collapse.py"]
)
