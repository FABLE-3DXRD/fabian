
import Numeric
from fabio import edfimage
#this will eventually come from fabio as well
from Fabian import image_file_series

class median_file_series:

  def __init__(self,filename,startnumber, filterlength, delta=1, quiet=1):
    self.filterlength=filterlength
    self.files=[]
    self.series=image_file_series.image_file_series(filename)
    self.series.jump(startnumber)
    self.files.append(self.series.current(toPIL=False))
    if not quiet: print self.series.filename
    for i in range(filterlength-1):
      self.series.next(steps=delta)
      self.files.append(self.series.current(toPIL=False))
      if not quiet: print self.series.filename
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
    e.header=edfimage.DEFAULT_VALUES
    e.header['col_end']=e.dim1-1
    e.header['row_end']=e.dim2-1
    e.header['DataType']='UnsignedShort'
    e.write(fname)
