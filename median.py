#!/usr/bin/env python -w

import image_file_series
import edfimage, tifimage, adscimage, brukerimage, marccdimage,bruker100image
import rocker
import Numeric

class median(rocker.rocker):
  def __init__(self,filename,startnumber,filterlength):
    print filename,startnumber,filterlength
    rocker.rocker.__init__(self,filename_sample=filename,startnumber=startnumber,endnumber=startnumber+filterlength-1)
    self.filterlength=filterlength
    #use the whole image as default - might want to do soem more clever thing at some pt
    d1,d2=self.series.current(toPIL=False).dim1,self.series.current(toPIL=False).dim2
    self.coord=(0,0,d1,d2)
    self.median=Numeric.zeros((d2,d1))
    self.filled=False

  def run(self):
    #for each image in the series add 
    flen=self.filterlength
    d1,d2=self.coord[2:]
    sorted=Numeric.zeros((flen,d2,d1))
    self.datastore=Numeric.zeros((flen,d2,d1))
    #fill up the filter
    if not self.filled:
      for i in range(flen):
	self.datastore[i,:,:]=self.series.current(toPIL=False).data
	self.series.next()
      self.filled=True
    self.setmedian()

  def setmedian(self):
    flen=self.filterlength
    if flen==0:
      self.median=self.datastore
      return
    #sort pxiels according to the image planes
    sorted=Numeric.sort(self.datastore,0)
    if flen%2==0:
      #filterlength is even - use the mean of the two central values
      self.median=0.5*(sorted[flen/2-1,...]+sorted[flen/2,...])
    else:
      self.median=sorted[flen/2-1,...]
      
  def slide(self):
    #slide filter one step
    self.series.next()
    newarr=self.series.current(toPIL=False).data
    store=self.datastore
    self.datastore=Numeric.concatenate((store[1:,...],Numeric.reshape(newarr,store[:1,...].shape)))
    self.setmedian()

  def write(self,fname):
    e=edfimage.edfimage()
    e.data=self.median
    e.dim2,e.dim1=self.median.shape
    e.header['Dim_1']=e.dim1
    e.header['Dim_2']=e.dim2
    e.header['col_end']=e.dim1-1
    e.header['row_end']=e.dim2-1
    e.write(fname)

if __name__=='__main__':
  def start():
    import sys,os,time
    b=time.clock()
    mf=median(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
    mf.run()
    mf.write('out1.edf');
    mf.slide()
    mf.write('out2.edf');
    e=time.clock()
    print (e-b)
  import profile
  profile.run('start()','profile_results')
  import pstats
  p=pstats.Stats('profile_results')
  p.sort_stats('cumulative').print_stats(40)
  


    
