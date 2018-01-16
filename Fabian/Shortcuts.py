from __future__ import absolute_import
try:
    from Tkinter import Tk, Frame, Message, X, Button, RIGHT
except:
    from tkinter import Tk, Frame, Message, X, Button, RIGHT
    
import Fabian
class show:
    def __init__(self):
        self.master = Tk()
        self.master.title('About fabian')
        frame = Frame(self.master, width=500, height=400, bd=1)
        frame.pack()

        frameAbout = Frame(frame, bd=0)
        message = \
"""
Key short cuts 

Main window:
  o - open new file
  q - quit application
  C - Close all opened windows 
  z - zoom in
  x - zoom out
  right arrow - next image
  left arrow  - previous image
  a - see "help - about"
  h - see "help - help"
  Change tools:
    F1 - activate zoom tool
    F2 - activate line profile tool
    F3 - activate intensity projections on vertical/horizontal box sides
    F4 - activate relief plot tool
    F5 - activate rocking curve tool
  Control peaks:
    p - show/hide peaks found by ImageD11 peaksearch
    c - clear peaks from memory
    r - read a peaks file (spt)
  Auto update images:
    f - activate/deactivate "File - auto file update"
    up-arrow   - add 0.5 sec. to time delay between 
                 loading files in auto file update mode
    down-arrow - subtract 0.5 sec. from the time delay
                 between loading files in auto file update mode

2D plot window:
  a - auto scale plot
  p - print/save plot
  q - quit 2D plot
"""

        Message(frameAbout, text=message,width=500).pack(fill=X, padx=5)
        frameAbout.pack(expand=1, pady=10, padx=5)

        frameAbout = Frame(frame, bd=0)
        Button(frameAbout,text='So what', bg='red', command=self.quit)\
                                          .pack(side=RIGHT)
        frameAbout.pack(expand=1, pady=10, padx=5)

    def quit(self):
        self.master.destroy()

