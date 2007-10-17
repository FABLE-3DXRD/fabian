#!/usr/bin/env python -w 
"""

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:erik.knudsen@risoe.dk
"""

import string

# fabio imports
from fabio import construct_filename,deconstruct_filename
from fabio import openimage

import re,os.path

class image_file_series:
  def __init__(self,filename=None):
    self.filename=filename
    stem,self.number=deconstruct_filename(filename)
    self.img=None
    self.noread=False
    
  def reset_series(self,filename,number=-1,filetype=None):
    num,ft=deconstruct_filename(filename)
    if filetype==None:
      self.filetype=ft
    else:
      self.filetype=filetype
    if number==-1:
      self.number=number
    else:
      self.number=num
   
  def __openimage(self,filename=None):
    if filename==None:
      filename=self.filename
    try:
      if self.noread:
        if not os.path.exists(filename):
          raise IOError, 'No such file or directory %s' % filename
      else:
        self.img = openimage.openimage(filename)
    except IOError:
      raise
   
  def current(self,toPIL=True):
    if not self.img:
      self.__openimage()
    if toPIL:
      return self.img.toPIL16()
    else:
      return self.img
      
  def next(self,steps=1):
    newnum=self.number+steps
    newfilename=construct_filename(self.filename,newnum)
    if newfilename==self.filename:
      raise ValueError,"new filename == old filename"
    try:
      self.__openimage(newfilename)#try to open that file
    except IOError:
      msg="No such file: %s " %(newfilename)
      raise IOError, msg
    #image loaded ok
    self.filename=newfilename
    self.number=newnum
    return True

  def prev(self,steps=1):
    newnum=self.number-steps
    newfilename=construct_filename(self.filename,newnum)
    if newfilename==self.filename:
      raise ValueError,"new filename == old filename"
    try:
      self.__openimage(newfilename)#try to open that file
    except IOError:
      newfilename=construct_filename(self.filename,newnum,padding=False)
      if newfilename==self.filename:
	raise ValueError,"new filename == old filename"
      try:
	#that didn't work - so try the unpadded version
	self.openimage(newfilename)
      except IOError:
        msg="No such file: %s " %(newfilename)
	raise IOError, msg
    #image loaded ok
    self.filename=newfilename
    self.number=newnum
    return True
  

  def jump(self,newnum,noconvert=False):
    newfilename=construct_filename(self.filename,newnum)
    try:
      self.__openimage(newfilename)#try to open that file
    except IOError:
      msg="No such file: %s " %(newfilename)
      raise IOError,msg
    #image loaded ok
    self.filename=newfilename
    self.number=newnum
    return True
  
  def loop(self,endnum=999999):
    #a generator for looping through the images in a series with a for loop
    num=self.number
    while num<endnum:
      yield(self.img)
      try:
	self.next()
      except IOError:
	break
      num=num+1
	

if __name__=='__main__':
  import sys,time
  b=time.clock()
  fs=file_series_iterator(sys.argv[1])
  print fs.filename,fs.current(toPIL=False)
  while fs.next() and fs.number<20:
    print fs.filename,fs.current(toPIL=False)
  e=time.clock()
  print (e-b)
