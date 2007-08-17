#!/usr/bin/env python 
"""

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:erik.knudsen@risoe.dk

"""

import Numeric
import math
from PIL import Image
import os

class edfimage:
  def __init__(self):
    self.data=None
    self.header={"ByteOrder":"LowByteFirst"}
    self.dim1=self.dim2=0
    self.m=self.maxval=self.stddev=self.minval=None
    self.header_keys=self.header.keys()
    self.bytecode=None
  
  def toPIL16(self,filename=None):
    if filename:
      self.read(filename)
    PILimage={
      'w':Image.frombuffer("F",(self.dim1,self.dim2),self.data,"raw","F;16",0,-1),
      'f':Image.frombuffer("F",(self.dim1,self.dim2),self.data.astype(Numeric.UInt16),"raw","F;16",0,-1),
      }[self.bytecode]
    return PILimage

  def readheader(self,fname):
    #only read the header of the file: useful for fast scanning for a header item
    f=self._open(fname)
    self._readheader(f)
    f.close()
    return self

  def _readheader(self,infile=None):
    ll=""
    while '}' not in ll:
      ll= ll+ infile.read(1024)
    ll.strip('{\n')
    for l in ll.split(';'):
      if '=' in l:
	(k,v)=l.split('=',1)
	self.header_keys.append(k.strip(' ;\n\r'))
	self.header[k.strip(' ;\n\r')]=v.strip(' ;\n\r')
  
  def _open(self,fname):
    # Check whether edf file has been compressed
    if os.path.splitext(fname)[1] == '.gz':
      import gzip
      f=gzip.GzipFile(fname,"rb")
    elif os.path.splitext(fname)[1] == '.bz2':
      import bz2
      f=bz2.BZ2File(fname,"rb")
    else:
      f=open(fname,"rb")
    return f

  def read(self,fname,verbose=0,padding='0'):
    #open the file and read the header
    f=self._open(fname)
    self._readheader(f)
    #read the rest of the file
    l=f.read()
    f.close()
    #check the datatype of the edffile (fit2d uses FLOAT for instance) default is 16 bit integer
    if 'DataType' in self.header_keys:
      if self.header['DataType'] in ('FLOAT','Float','FloatValue'):
        bytecode=Numeric.Float32
      else:
        bytecode=Numeric.UInt16
    else:
      bytecode=Numeric.UInt16 # Default bytecode if none given
    bpp={Numeric.UInt16:2,Numeric.Float32:4} [bytecode]
    
    #now read the data into the array
    (self.dim1,self.dim2)=int(self.header['Dim_1']),int(self.header['Dim_2'])
    if len(l)!=self.dim1*self.dim2*bpp:
      missing_bytec=self.dim2*self.dim1*bpp-len(l)
      if missing_bytec>0:
	l=l+padding*missing_bytec
	print 'warning: Size spec in edf-header does not match size of image data field - padding with %d' % missing_bytec,padding,'s'
      else:
	l=l[:missing_bytec]
	print 'warning: Size spec in edf-header does not match size of image data field - %d byte(s) on end not read. Please check for image corruption.' % -missing_bytec
	
    if 'Low' in self.header['ByteOrder']:
      try:
	self.data=Numeric.reshape(Numeric.fromstring(l,bytecode),[self.dim2, self.dim1])
      except ValueError:
	raise IOError, 'Size spec in edf-header does not match size of image data field'
      self.bytecode=bytecode
      if verbose: print 'using low byte first (x386-order)'
    else:
      try:
	self.data=Numeric.reshape(Numeric.fromstring(l,bytecode),[self.dim2, self.dim1]).byteswapped()
      except ValueError:
	raise IOError, 'Size spec in edf-header does not match size of image data field'
      self.bytecode=bytecode
      if verbose: print 'using high byte first (network order)'
    self.resetvals()
    return self

  def getheader(self):
    if self.header=={}:
      print "No file loaded"
    return self.header
  
  def getmax(self):
    if self.maxval==None:
      max_xel=Numeric.argmax(Numeric.ravel(self.data))
      self.maxval=Numeric.ravel(self.data)[max_xel]
    return int(self.maxval)
  
  def getmin(self):
    if self.minval==None:
      min_xel=Numeric.argmin(Numeric.ravel(self.data))
      self.minval=Numeric.ravel(self.data)[min_xel]
    return int(self.minval)

  def integrate_area(self,coords,floor=0):
    if self.data==None:
      return 0
    else:
      if coords[0]>coords[2]:
	coords[0:3:2]=[coords[2],coords[0]]
      if coords[1]>coords[3]:
	coords[1:4:2]=[coords[3],coords[1]]
      #normally coordinates are given as (x,y) whereas a matrix is given as row,col
      #also the (for whichever reason) the image is flipped upside down wrt to the matrix
      # hence these tranformations
      c=(self.dim2-coords[3]-1,coords[0],self.dim2-coords[1]-1,coords[2])
      # avoid overflows
      S=Numeric.sum(Numeric.ravel(self.data[int(c[0]):int(c[2])+1,int(c[1]):int(c[3])+1].astype(Numeric.Float32)))
      
      S=S-floor*(1+c[2]-c[0])*(1+c[3]-c[1])
    return S

  def getmean(self):
    if self.m==None:
      self.m=Numeric.sum(Numeric.ravel(self.data.astype(Numeric.Float)))/(self.dim1*self.dim2)
    return float(self.m)
    
  def getstddev(self):
    if self.m==None:
      self.getmean()
      print "recalc mean"
    if self.stddev==None:
      N=self.dim1*self.dim2-1
      S=Numeric.sum(Numeric.ravel((self.data.astype(Numeric.Float)-self.m)/N*(self.data.astype(Numeric.Float)-self.m)) )
      self.stddev=S/(self.dim1*self.dim2-1)
    return float(self.stddev)

  def add(self, otherImage):
    if not hasattr(otherImage,'data'):
      print 'edfimage.add() called with something that does not have a data field'
    try:
      self.data=Numeric.clip(self.data+otherImage.data,0,65535)
    except:
      message='incompatible images - Do they have the same size?'
      
  def resetvals(self):
    self.m=self.stddev=self.maxval=self.minval=None
  
  def rebin(self,x_rebin_fact,y_rebin_fact):
    if self.data==None:
      print 'Please read the file you wish to rebin first'
      return
    (mx,ex)=math.frexp(x_rebin_fact)
    (my,ey)=math.frexp(y_rebin_fact)
    if (mx!=0.5 or my!=0.5):
      print 'Rebin factors not power of 2 not supported (yet)'
      return
    if int(self.dim1/x_rebin_fact)*x_rebin_fact!=self.dim1 or int(self.dim2/x_rebin_fact)*x_rebin_fact!=self.dim2:
      print 'image size is not divisible by rebin factor - skipping rebin'
      return
    self.data.savespace(1)#avoid the upcasting behaviour
    i=1
    while i<x_rebin_fact:
      self.data=((self.data[:,::2]+self.data[:,1::2])/2)
      i=i*2
    i=1
    while i<y_rebin_fact:
      self.data=((self.data[::2,:]+self.data[1::2,:])/2)
      i=i*2
    self.resetvals()
    self.dim1=self.dim1/x_rebin_fact
    self.dim2=self.dim2/y_rebin_fact
    #update header
    self.header['Dim_1']=self.dim1
    self.header['Dim_2']=self.dim2
    self.header['col_end']=self.dim1-1
    self.header['row_end']=self.dim2-1
  
  def write(self,fname):
    f=open(fname,"wb")
    f.write('{\n')
    i=4
    for k in self.header_keys:
      out = (("%s = %s;\n") % (k,self.header[k]))
      i = i + len(out)
      f.write(out)
    #if additional items in the header just write them out in the order they happen to be in
    for k,v in self.header.iteritems():
      if k in self.header_keys: continue
      out = (("%s = %s;\n") % (k,self.header[k]))
      i = i + len(out)
      f.write(out)
    out = (4096-i)*' '
    f.write(out)
    f.write('}\n')
    if self.header["ByteOrder"]=="LowByteFirst":
      f.write(self.data.astype(Numeric.UInt16).tostring())
    else:
      f.write(self.data.byteswapped().astype(Numeric.UInt16).tostring())
    f.close()

if __name__=='__main__':
  import sys,time
  I=edfimage()
  b=time.clock()
  while (sys.argv[1:]):
    I.read(sys.argv[1])
    r=I.toPIL16()
    I.rebin(2,2)
    I.write('jegErEnFil0000.edf')
    print sys.argv[1] + (": max=%d, min=%d, mean=%.2e, stddev=%.2e") % (I.getmax(),I.getmin(), I.getmean(), I.getstddev()) 
    print 'integrated intensity (%d %d %d %d) =%.3f' % (10,20,20,40,I.integrate_area((10,20,20,40)))
    sys.argv[1:]=sys.argv[2:]
  e=time.clock()
  print (e-b)
