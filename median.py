#!/usr/bin/env python -w

import image_file_series
import edfimage, tifimage, adscimage, brukerimage, marccdimage,bruker100image
import rocker
import Numeric

class median_file_series:

  def __init__(self,filename,startnumber, filterlength, delta=1):
    self.filterlength=filterlength
    self.files=[]
    self.series=image_file_series.image_file_series(filename)
    self.series.jump(startnumber)
    self.files.append(self.series.current(toPIL=False))
    print self.series.filename
    for i in range(filterlength-1):
      self.series.next(steps=delta)
      self.files.append(self.series.current(toPIL=False))
      print self.series.filename
    d1,d2=self.files[0].dim1,self.files[0].dim2
    self.median=Numeric.zeros((d2,d1)).astype(Numeric.Float)
  
  def reset(self,number,delta=1):
    self.files=[]
    print 'i want to jump to',number
    self.series.jump(number)
    for i in range(self.filterlength):
      self.series.next(steps=delta)
      self.files.append(self.series.current(toPIL=False))
      print self.series.filename
    
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

  def slide(self,steps=1,delta=1):
    print 'slide', steps, self.filterlength 
    if steps+1000<self.filterlength:
      for i in range(steps):
        print i
        #pop the first element of the filelist
        self.files.pop()
        #append the next one
        self.series.next(steps=delta)
        #read its data
        self.files.append(self.series.current(toPIL=False))
        #reevaluate median
      self.run()
    else:
      print 'sliding would be inefficient - doing a jump instead'
      self.reset(self.series.number+(steps-self.filterlength)*delta,delta=delta)
      self.run()
    
  def write(self,fname):
    e=edfimage.edfimage()
    e.data=self.median
    e.dim2,e.dim1=self.median.shape
    e.header['Dim_1']=e.dim1
    e.header['Dim_2']=e.dim2
    e.header['col_end']=e.dim1-1
    e.header['row_end']=e.dim2-1
    e.header['DataType']='UnsignedShort'
    e.write(fname)
  


if __name__=='__main__':
  def start():
    import sys,os,time
    b=time.clock()
    mf=median_file_series(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),delta=int(sys.argv[4]))
    mf.run()
    mf.write('med1.edf');
    mf.slide(int(sys.argv[3]),int(sys.argv[4]))
    mf.write('med2.edf');
    mf.slide(int(sys.argv[3]),int(sys.argv[4]))
    mf.write('med3.edf');
    print (time.clock()-b)
  import profile
  profile.run('start()','profile_results')
  import pstats
  p=pstats.Stats('profile_results')
  p.sort_stats('cumulative').print_stats(40)
  


    
