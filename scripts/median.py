#!/usr/bin/env python
from Fabian.median import median_file_series

if __name__=='__main__':
  def start():
    import sys,os,time
    b=time.clock()
    #mf=median_file_series(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),delta=int(sys.argv[4]))
    mf=median_file_series(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
    mf.run()
    mf.write('median_image.edf');
    #mf.slide(int(sys.argv[3]),int(sys.argv[4]))
    #mf.write('med2.edf');
    #mf.slide(int(sys.argv[3]),int(sys.argv[4]))
    #mf.write('med3.edf');
    print (time.clock()-b)
  start()
    
