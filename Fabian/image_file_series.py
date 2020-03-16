#!/usr/bin/env python -w 
"""

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:erik.knudsen@risoe.dk
"""

from __future__ import absolute_import
from __future__ import print_function
import string

# fabio imports
# from fabio import construct_filename,deconstruct_filename
from fabio import openimage
import fabio

import re,os.path

class image_file_series:
  def __init__(self,filename=None):
    self.filename=filename
    self.number=fabio.extract_filenumber(filename)
    self.img=None
    self.noread=False
    
  def reset_series(self,filename,number=-1,filetype=None):
    fo=deconstruct_filename(filename)
    filetype = fo.format
    number = fo.num
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
          raise IOError('No such file or directory %s' % filename)
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
    newfilename=fabio.jump_filename(self.filename,newnum)
    if newfilename==self.filename:
      raise ValueError("new filename == old filename")
    try:
      self.__openimage(newfilename)#try to open that file
    except IOError:
      msg="No such file: %s " %(newfilename)
      raise IOError(msg)
    #image loaded ok
    self.filename=newfilename
    self.number=newnum
    return True

  def prev(self,steps=1):
    newnum=self.number-steps
    newfilename=fabio.jump_filename(self.filename,newnum)
    if newfilename==self.filename:
      raise ValueError("new filename == old filename")
    try:
      self.__openimage(newfilename)#try to open that file
    except IOError:
      newfilename=fabio.jump_filename(self.filename,newnum,padding=False)
      if newfilename==self.filename:
        raise ValueError("new filename == old filename")
      try:
        #that didn't work - so try the unpadded version
        self.openimage(newfilename)
      except IOError:
        msg="No such file: %s " %(newfilename)
        raise IOError(msg)
    #image loaded ok
    self.filename=newfilename
    self.number=newnum
    return True
  

  def jump(self,newnum,noconvert=False):
    #FIXME - convert ???
    newfilename=fabio.jump_filename(self.filename,newnum)
    try:
      self.__openimage(newfilename)#try to open that file
    except IOError:
      msg="No such file: %s " %(newfilename)
      raise IOError(msg)
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
        next(self)
      except IOError:
        break
      num=num+1


if __name__=='__main__':
  import sys,time
  b=time.time()
  fs=image_file_series(sys.argv[1])
  print(fs.filename,fs.current(toPIL=False))
  while next(fs) and fs.number<20:
    print(fs.filename,fs.current(toPIL=False))
  e=time.time()
  print((e-b))
