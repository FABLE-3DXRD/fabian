#! /usr/bin/env python
"""
Adds up a series of diffraction images, subtracts the background and writes out an edf file called pseudopowder2D.edf

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:henning.sorensen@risoe.dk, erik.knudsen@risoe.dk
"""
import numpy as N
from Fabian import image_file_series
from fabio import edfimage
from fabio import openimage

class collapse:
  def __init__(self, filename_sample=None, startnumber=0, endnumber=-1,bgimage=None):
    #setup the file sequence
    self.series=image_file_series.image_file_series(filename_sample)
    self.series.jump(startnumber)
    self.start=startnumber
    self.end=endnumber
    d1=self.series.current(toPIL=False).dim1
    d2=self.series.current(toPIL=False).dim2
    self.header = self.series.current(toPIL=False).getheader()
    self.coord=(0,0,d1,d2)
    if bgimage is not None:
      self.bgimage=bgimage.astype(N.int32)
    else:
      self.bgimage = None
    self.total_image=N.zeros((d2,d1),N.float32)
    self.data=N.zeros((endnumber-startnumber+1))

  def newstart(self,start):
    #jump to a new starting number
    try:
      self.series.jump(start)
    except (ValueError,IOError), msg:
      print msg, '-aborted'
      raise
    self.start=start
    
  def run(self):
    for i in range(len(self.data)):
      self.total_image=self.total_image+self.series.current(toPIL=False).data
      #self.data[i]=series.current(toPIL=False).integrate_area(self.coord)
      if i < len(self.data)-1:
        try:
          self.series.next()
	  #if theres an error opening the file just skip over it
        except (ValueError,IOError), msg:
          print msg, '- aborted!'
          break
    if self.bgimage is not None: 
      self.total_image=self.total_image-len(self.data)*self.bgimage

    # Scale image
    im_max = N.argmax(N.ravel(self.total_image))
    max_val = (2**16-1)*1.0/im_max
    self.total_image = self.total_image*max_val
    # set pixels with a value < 0 to 0, and values > 16bit to 16bit
    self.total_image = N.clip(self.total_image,0, 2**16-1)
    
  def getdata(self):
    #return the array containing the rocking curve
    return self.total_image

  def write(self,fname):
    e=edfimage.edfimage()
    e.data=self.total_image
    e.dim2,e.dim1=self.total_image.shape
    e.header = self.header
    e.header['Dim_1']=e.dim1
    e.header['Dim_2']=e.dim2
    e.header['col_end']=e.dim1-1
    e.header['row_end']=e.dim2-1
    e.header['DataType']='UnsignedShort'
    e.header['Image']=1
    e.write(fname)


if __name__=='__main__':
  import sys,time
  from string import atoi
  b=time.clock()
  try:
    bgimage = openimage.openimage(sys.argv[4])
    bgim = bgimage.data
  except:
    bgim = None
  R=collapse(filename_sample=sys.argv[1],startnumber=atoi(sys.argv[2]),endnumber=atoi(sys.argv[3]),bgimage=bgim)
  R.run()
  R.write('pseudopowder2D.edf')
#  print R.getdata()
  e=time.clock()
  print (e-b)

