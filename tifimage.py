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
import Numeric

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
      PILimage = self.data#.convert('I')
      return PILimage
    else:
      # For some odd reason the getextrema does not work on unsigned 16 bit
      # but it does on 32 bit images, hence convert
      PILimage = self.data#.convert('I')
      return PILimage
	
  def read(self,fname,verbose=0):
    print fname
    self.data=Image.open(fname).convert('I')
    print self.data
    (self.dim1, self.dim2) = self.data.size
  
  def write(self):
    pass
    
  def getmean(self):
    if self.m==None:
      l=list(self.data.getdata())
      self.m=sum(l)/len(l)
    return float(self.m)
  
  def getmax(self):
    if self.maxval==None or self.minval==None:
      self.minval,self.maxval = self.data.getextrema()
    return self.maxval

  def getmin(self):
    if self.maxval==None or self.minval==None:
      self.minval,self.maxval = self.data.getextrema()
    return self.minval
  
  def getstddev(self):
    if self.stddev==None:
      self.getmean()
      N=self.dim1*self.dim2-1
      l=list(self.data.getdata())
      l=map(lambda i: (i-self.m)*(i-self.m),l)
      S=sum(l)/N
      self.stddev=S
    return self.stddev
    
  def rebin(self,x_rebin_factor, y_rebin_factor):
    print "rebinning not implemented - yet!"
