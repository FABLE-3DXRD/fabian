#!/usr/bin/env python 
"""

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:henning.sorensen@risoe.dk

"""

from PIL import Image

class tifimage:
  data=None
  header={}
  dim1=dim2=0
  m=maxval=stddev=minval=None
  header_keys=[]
  bytecode=None
  
  def toPIL32(self,filename=None):
    if filename:
      self.read(filename)
      # For some odd reason the getextrema does not work on unsigned 16 bit
      # but it does on 32 bit images, hence convert
      PILimage = self.data.convert('I')
      return PILimage
    else:
      # For some odd reason the getextrema does not work on unsigned 16 bit
      # but it does on 32 bit images, hence convert
      PILimage = self.data.convert('I')
      return PILimage
	
  def read(self,fname,verbose=0):
    print fname
    self.data=Image.open(fname)
    print self.data
    (self.dim1, self.dim2) = self.data.size
    
