#!/usr/bin/env python
from distutils.core import setup
import sys

if 'win' == sys.platform[:3]:
  import py2exe, glob
  print "doing the windows thing"
  setup(windows=['fabian.py'],
	options = {"py2exe":{
		"bundle_files": 3,
		"compressed": 1,
                "includes": 'matplotlib',
                "excludes": ['_gtkagg'],
                "dll_excludes": ['libgdk-win32-2.0-0.dll','libgobject-2.0-0.dll']
		}}
        data_files = [(r'matplotlibdata', glob.glob(r'c:\python24\share\matplotlib\*')),
                      (r'matplotlibdata', [r'c:\python24\share\matplotlib\.matplotlibrc'])],
	)
else:
  setup(name='fabian',
        version='0.1',
        description='Image viewer for file series of diffraction images',
        license='GPL',
        maintainer='Henning Osholm Soerensen and Erik Knudsen',
        maintainer_email='henning.sorensen@risoe.dk or erik.knudsen@risoe.dk',
        url='http://fable.sourceforge.net',
        py_modules=['edfimage','tifimage','adscimage','brukerimage','bruker100image',
                    'marccdimage','pnmimage','pixel_trace','rocker','image_file_series'],
        scripts=["fabian.py"])

