#! /usr/bin/env python
"""

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:henning.sorensen@risoe.dk
"""
from __future__ import absolute_import
from __future__ import print_function
from Fabian import image_file_series

class rocker:
  #class to perform a rocking curve over a set of coordinates and a file sequence"
  def __init__(self, coord=[0,0,0,0], filename_sample=None, startnumber=0, endnumber=-1):
    #setup the file sequence
    self.series=image_file_series.image_file_series(filename_sample)
    self.series.jump(startnumber)
    self.start=startnumber
    self.end=endnumber
    self.coord=tuple(coord)
    self.data=[0]*(endnumber-startnumber+1)
    self.imagenumber=[0]*(endnumber-startnumber+1)

  def newstart(self,start):
    #jump to a new starting number
    try:
      self.series.jump(start)
    except (ValueError,IOError) as msg:
      print(msg, '-aborted')
      raise
    self.start=start
    
  def run(self):
    series=self.series
    for i in range(len(self.data)):
      self.data[i]=series.current(toPIL=False).integrate_area(self.coord)
      self.imagenumber[i] = series.number
      if i < len(self.data)-1:
        try:
          series.next()
          #if there's an error opening the file just skip over it
        except (ValueError,IOError) as msg:
          print(msg, '- aborted!')
          break
	
  def getdata(self):
    #return the array containing the rocking curve
    return self.data

if __name__=='__main__':
  import sys,time
  from string import atoi
  b=time.time()
  c=[atoi(sys.argv[4]),atoi(sys.argv[5]),atoi(sys.argv[6]),atoi(sys.argv[7])]
  R=rocker(filename_sample=sys.argv[1],coord=c,startnumber=atoi(sys.argv[2]),endnumber=atoi(sys.argv[3]))
  R.run()
  print(R.getdata())
  e=time.time()
  print((e-b))

