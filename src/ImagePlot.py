from Tkinter import *

from numpy import sort,array
from tkFileDialog import asksaveasfilename
import matplotlib
matplotlib.use('TkAgg')
try:
    matplotlib.rcParams['numerix'] = 'numpy'
except:
    print "Might have a problem with matplotlib configuration"
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib.transforms as transforms


#import pylab as plt

class imagePlot:
  def __init__(self,master,title='Plot',x=None,y=None,ptitle='',x2=None,y2=None,ptitle2=''):
      self.master = master
      self.master.title(title)
      self.master.bind('q',self.quit)
      self.master.bind('a',self.autoscale)
      self.master.bind('p',self.print_canvas)
      self.frame = Frame(self.master)
      self.frame.pack()
      self.f = Figure(figsize=(8,5), dpi=100)
#      #self.f.subplots_adjust(hspace = .2)
      self.plotcanvas = FigureCanvasTkAgg(self.f, master=self.master)
      self.plotcanvas.show()
      self.plotcanvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
      #Make control and info box below canvas
      frameInfo = Frame(self.master, bd=0)
      frameInfo.pack(side=BOTTOM,fill=X)
      Button(frameInfo,text='print', 
             bg='white', 
             command=self.print_canvas).pack(side=LEFT,padx=2)
      
      Button(frameInfo,text='reset', 
             bg='white', 
             command=self.autoscale).pack(side=LEFT,padx=2)
      
      # Show mouse coordinates
      self.ShowCoor_y = Label(frameInfo, text='    0', width =7, 
                          bg ='white',bd=0, relief=RIDGE, anchor=W)
      self.ShowCoor_y.pack(side=RIGHT, pady = 2)
      self.ShowCoor_comma = Label(frameInfo, text=', ', width =2, 
                          bg ='white',bd=0, relief=RIDGE, anchor=W)
      self.ShowCoor_comma.pack(side=RIGHT, padx = 0)
      self.ShowCoor_x = Label(frameInfo, text='    0,', width =8, 
                          bg ='white',bd=0, relief=RIDGE, anchor=W)
      self.ShowCoor_x.pack(side=RIGHT, padx = 0)

      # One plot of two subplots ?
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
        self.f.canvas.mpl_connect('motion_notify_event', self.MouseMotion)
        self.f.canvas.mpl_connect('button_press_event',self.start_corner)
        self.f.canvas.mpl_connect('button_release_event',self.end_corner)

  # Mouse controls 
  def start_corner(self,event):
    if event.xdata != None and event.ydata != None:
        self.corner1 = [event.xdata, event.ydata]
        wid = 0
        hei = 0
        self.rect = patches.Rectangle(self.corner1,wid,hei,alpha=0.2) 
        self.a.add_patch(self.rect)
        self.f.canvas.draw()

  def end_corner(self,event):
    if event.xdata != None and event.ydata != None:
        self.corner2 = [event.xdata, event.ydata]
        xlim = sort([self.corner2[0],self.corner1[0]])
        ylim = sort([self.corner2[1],self.corner1[1]])
        self.a.set_xlim(xlim)
        self.a.set_ylim(ylim)
        self.rect.remove()
        self.f.canvas.draw()

  def MouseMotion(self,event):
    if event.xdata != None:
        x='%6g' %event.xdata
        self.ShowCoor_x.config(text=x)
    if event.ydata != None:
        y='%6g' %event.ydata
        self.ShowCoor_y.config(text=y)

    if event.button == 1 and event.xdata != None and event.ydata != None:
        self.corner2 = [event.xdata, event.ydata]
        wid = self.corner2[0]-self.corner1[0]
        hei = self.corner2[1]-self.corner1[1]
        self.rect.set_width(wid)
        self.rect.set_height(hei)
        self.f.canvas.draw()

  def autoscale(self,event=None):
    """
    Rescale plot to auto range
    """
    self.a.autoscale_view()
    self.f.canvas.draw()
    
  def print_canvas(self,event=None):
      """
      print the plot on the canvas to a file
      """
      fname = asksaveasfilename(filetypes=[
              ("png", "*.png"),
              ("pdf", "*.pdf"),
              ("eps", "*.eps"),
              ("ps", "*.ps"),
              ("All Files", "*")])
      self.f.canvas.print_figure(fname)

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

