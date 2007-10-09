from Tkinter import *

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class imagePlot:
  def __init__(self,master,title='Plot',x=None,y=None,ptitle='',x2=None,y2=None,ptitle2=''):
      self.master = master
      self.master.title(title)
      self.master.bind('q',self.quit)
      self.frame = Frame(self.master)
      self.frame.pack()
      self.f = Figure(figsize=(8,5), dpi=100)
      #self.f.subplots_adjust(hspace = .2)
      self.plotcanvas = FigureCanvasTkAgg(self.f, master=self.master)
      self.plotcanvas.show()
      self.plotcanvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
      if x2 != None and y2 !=None:
        self.a = self.f.add_subplot(211)
        self.a.plot(x, y, 'b-')
        self.a.set_title(ptitle)
        self.b = self.f.add_subplot(212)
        self.b.plot(x2, y2, 'b-')
        self.b.set_title(ptitle2)
      else:
        self.a = self.f.add_subplot(111)
        self.a.plot(x, y, ptitle)
        self.a.set_title(ptitle)

  def setbindings(self):
    pass

  def quit(self,event=None):
    self.master.destroy()

  def update(self,coord=[0,0,0,0],zoomarea=[0,0,0,0],zoomfactor=1, newimage=None):
      from Fabian import pixel_trace
      t=coord
      
      corners=[(zoomarea[0]+t[0]/zoomfactor), (zoomarea[1]+t[1]/zoomfactor), (zoomarea[0]+t[2]/zoomfactor), (zoomarea[1]+t[3]/zoomfactor)]
      pixels = pixel_trace.pixel_trace(corners)
      t = []
      pixval = []
      path = 0
      for i in range(len(pixels)):
        path = path + pixels[i][2]
        t.append(i)
        pixval.append(newimage.getpixel((pixels[i][0],pixels[i][1])))
      self.a.clear()
      self.a.plot(t, pixval, 'b-')
      self.plotcanvas.show()


class imagePlot2:
  def __init__(self,master,title='Plot',x=None,y=None,ptitle='',x2=None,y2=None,ptitle2=''):
      self.master = master
      self.master.title(title)
      self.master.bind('q',self.quit)
      self.frame = Frame(self.master)
      self.frame.pack()
      self.f = Figure(figsize=(8,5), dpi=100)
      #self.f.subplots_adjust(hspace = .2)
      self.plotcanvas = FigureCanvasTkAgg(self.f, master=self.master)
      self.plotcanvas.show()
      self.plotcanvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
      if x2 != None and y2 !=None:
        self.a = self.f.add_subplot(211)
        self.a.plot(x, y, 'b-')
        self.a.set_title(ptitle)
        self.b = self.f.add_subplot(212)
        self.b.plot(x2, y2, 'b-')
        self.b.set_title(ptitle2)
      else:
        self.a = self.f.add_subplot(111)
        self.a.plot(x, y, ptitle)
        self.a.set_title(ptitle)

  def setbindings(self):
    pass

  def quit(self,event=None):
    self.master.destroy()

  def update(self,coord=[0,0,0,0],zoomarea=[0,0,0,0],zoomfactor=1, newimage=None):
      from Fabian import pixel_trace
      t=coord
      corners=[int(zoomarea[0]+t[0]/zoomfactor), int(zoomarea[1]+t[1]/zoomfactor), int(zoomarea[0]+t[2]/zoomfactor), int(zoomarea[1]+t[3]/zoomfactor)]
      xbins = []
      ybins = []
      xvalues = []
      yvalues = []
      for x in range(corners[0],corners[2]):
        y_int = 0
        xbins.append(x)
        for y in range(corners[1],corners[3]):
          y_int = y_int + newimage.getpixel((x,y))
        yvalues.append(y_int)

      for y in range(corners[1],corners[3]):
        x_int = 0
        ybins.append(y)
        for x in range(corners[0],corners[2]):
          x_int = x_int + newimage.getpixel((x,y))
        xvalues.append(x_int)

      self.a.clear()
      self.b.clear()
      self.a.plot(xbins, yvalues, 'b-')
      self.b.plot(ybins, xvalues, 'b-')
      self.plotcanvas.show()

