#!/usr/bin/env python -w

import image_file_series
import edfimage, tifimage, adscimage, brukerimage, marccdimage,bruker100image
import rocker
import Numeric


class median_file_series:

  def __init__(self,filename,startnumber, filterlength):
    print filename,startnumber,filterlength
    self.filterlength=filterlength
    self.files=[]
    self.series=image_file_series.image_file_series(filename)
    self.series.jump(startnumber)
    for i in range(filterlength):
      self.files.append(self.series.current(toPIL=False))
      self.series.next()
    print 'initial series from',startnumber,'to',self.series.number-1
    d1,d2=self.files[0].dim1,self.files[0].dim2
    self.median=Numeric.zeros((d2,d1)).astype(Numeric.Float)
  
  def reset(self,number):
    self.files=[]
    print 'i want to jump to',number
    self.series.jump(number)
    for i in range(self.filterlength):
      self.files.append(self.series.current(toPIL=False))
      self.series.next()
    
  def run(self):
      flen=self.filterlength
      d1,d2=self.files[0].dim1,self.files[0].dim2
      sorted=Numeric.zeros((flen,d1))
      for i in range(d2):
	j=0
	for im in self.files:
          sorted[j,:]=im.data[i,:]
          j=j+1
	sorted=Numeric.sort(sorted,0)
	if flen%2==0:
          #filterlength is even - use the mean of the two central values
          self.median[i,:]=0.5*(sorted[flen/2-1,...]+sorted[flen/2,...])
	else:
          self.median[i,:]=sorted[flen/2-1,...]

  def slide(self,steps=1):
    if steps<self.filterlength:
      for i in range(steps):
        print i
        #pop the first element of the filelist
        self.files.pop()
        #append the next one
        self.series.next()
        #read its data
        self.files.append(self.series.current(toPIL=False))
        #reevaluate median
      self.run()
    else:
      print 'sliding would inefficient - doing a jump instead'
      self.reset(self.series.number-self.filterlength+steps)
      self.run()
    
  def write(self,fname):
    e=edfimage.edfimage()
    e.data=self.median
    e.dim2,e.dim1=self.median.shape
    e.header['Dim_1']=e.dim1
    e.header['Dim_2']=e.dim2
    e.header['col_end']=e.dim1-1
    e.header['row_end']=e.dim2-1
    e.write(fname)
  

    
      
class median(rocker.rocker):
  def __init__(self,filename,startnumber,filterlength):
    print filename,startnumber,filterlength
    rocker.rocker.__init__(self,filename_sample=filename,startnumber=startnumber,endnumber=startnumber+filterlength-1)
    self.filterlength=filterlength
    #use the whole image as default - might want to do something more clever thing at some pt
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
    #sort pixels according to the image planes
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
    mf=median_file_series(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
    mf.run()
    mf.write('out1.edf');
    mf.slide(int(sys.argv[3]))
    mf.write('out2.edf');
    mf.slide(int(sys.argv[3]))
    mf.write('out3.edf');
    e=time.clock()
    print (e-b)
  #start()
  import profile
  profile.run('start()','profile_results')
  import pstats
  p=pstats.Stats('profile_results')
  p.sort_stats('cumulative').print_stats(40)
  


    
