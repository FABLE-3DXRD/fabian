
import numpy as N
from fabio import edfimage
#this will eventually come from fabio as well
from Fabian import image_file_series

class median_file_series:

  def __init__(self,filename,startnumber, filterlength, delta=1, debug=1):
    self.filterlength = filterlength
    self.files = []
    self.debug = debug
    self.series = image_file_series.image_file_series(filename)
    try:
      self.series.jump(startnumber)
      self.files.append(self.series.current(toPIL=False))
      skipping = 0
    except:
      skipping = 1
      print 'warning file does not exist'
      raise
    if self.debug: print self.series.filename
    
    for i in range(filterlength-1):
      try:
        self.series.next(steps=delta+skipping)
        self.files.append(self.series.current(toPIL=False))
        skipping = 0
      except KeyboardInterrupt:
        raise
      except:
        print 'warning file does not'
        skipping += 1
        raise
      if self.debug: print self.series.filename
    d1,d2=self.files[0].dim1,self.files[0].dim2
    print len(self.files)
    self.median=N.zeros((d2,d1)).astype(N.float)
  
  def reset(self,number,delta=1):
    self.files=[]
    if self.debug: print 'i want to jump to',number
    self.series.jump(number)
    skipping = 0
    for i in range(self.filterlength):
      try:
        self.series.next(steps=delta+skipping)
        self.files.append(self.series.current(toPIL=False))
        skipping = 0
      except:
        skipping += 1
      if self.debug: print self.series.filename
    
  def run(self):
      flen=len(self.files)
      print flen
      d1,d2=self.files[0].dim1,self.files[0].dim2
      sorted=N.zeros((flen,d1))
      for i in range(d2):
        j=0
        for im in self.files:
          sorted[j,:]=im.data[i,:]
          j=j+1
        sorted=N.sort(sorted,0)
        if flen%2==0:
          #filterlength is even - use the mean of the two central values
          self.median[i,:]=0.5*(sorted[flen/2-1,...]+sorted[flen/2,...])
        else:
          self.median[i,:]=sorted[flen/2-1,...]

  def slide(self,steps=1,delta=1):
    if steps+1000<self.filterlength:
      for i in range(steps):
        #pop the first element of the filelist
        self.files.pop()
        #append the next one
        self.series.next(steps=delta)
        #read its data
        self.files.append(self.series.current(toPIL=False))
        #reevaluate median
      self.run()
    else:
      if self.debug: print 'sliding would be inefficient - doing a jump instead'
      print 'NO: ',self.series.number+(steps-self.filterlength)*delta
      print self.filterlength,delta,self.series.number
      self.reset(self.series.number+(steps-self.filterlength)*delta,delta=delta)
      self.run()
    
  def write(self,fname,header = None):
    if self.debug: print 'write median image to', fname
    e=edfimage.edfimage()
    e.data=N.clip(self.median,0, 2**16-1)
    e.data = e.data.astype(N.uint16)
    #e.header=edfimage.DEFAULT_VALUES
    #e.header['DIM_1']=e.dim1
    #e.header['DIM_2']=e.dim2

    #e.header['col_end']=e.dim1-1
    #e.header['row_end']=e.dim2-1
    #e.header['DataType']='UnsignedShort'
    if header != None:
      for arg in header:
        e.header[arg] = header[arg]    
    e.write(fname)
