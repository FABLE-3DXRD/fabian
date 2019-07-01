#! /usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
try:
    from Tkinter import *
except:
    from tkinter import *
from Fabian import appWin

##########################
#   Main                 #
##########################
if __name__=='__main__':
    from Fabian import appWin
    import sys
    def start():
        import time
        t1=time.time()
        if len(sys.argv) > 2:
            print("Only the first file will be opened")
        if len(sys.argv) >= 2:
            f=sys.argv[1]
        else:
            f=None
  
        root=Tk()
        mainwin = appWin.appWin(root,filename=f,zoomfactor=0.5,mainwin='yes')
    
        t2=time.time()
        print("time:",t2-t1)
        root.mainloop()
    start()
