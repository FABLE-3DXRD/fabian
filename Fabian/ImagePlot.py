from __future__ import absolute_import
try:
  from Tkinter import *
  from tkFileDialog import asksaveasfilename
except:
  # py3
  from tkinter import *
  from tkinter.filedialog import asksaveasfilename

from numpy import sort,array

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib.transforms as transforms

class common_plot:
  """
  Common functions used for all plot types
  """
  def __init__(self,master,title='Plot',
               x=None,y=None,ptitle='',x2=None,y2=None,ptitle2=''):
      self.master = master
      self.master.title(title)
      self.master.bind('q',self.quit)
      self.master.bind('a',self.autoscale)
      self.master.bind('p',self.print_canvas)
      self.refpoint = None
      self.act_plot = None
      self.frame = Frame(self.master)
      self.frame.pack()
      self.f = Figure(figsize=(8,5), dpi=100)
      #self.f.subplots_adjust(hspace = .2)
      self.plotcanvas = FigureCanvasTkAgg(self.f, master=self.master)
      if not hasattr( self.plotcanvas, "show"):
        # show went away in recent matplotlibs...
        self.plotcanvas.show = self.plotcanvas.draw
      self.plotcanvas.show()
      self.plotcanvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
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
      self.subplot = [0,0]
      
      if x2 != None and y2 !=None:
        self.subplot[0] = self.f.add_subplot(211)
        self.subplot[0].plot(x, y, 'b-')
        self.subplot[0].set_title(ptitle)
        self.subplot[1] = self.f.add_subplot(212)
        self.subplot[1].plot(x2, y2, 'b-')
        self.subplot[1].set_title(ptitle2)
      else:
        self.subplot = [0]
        self.subplot[0] = self.f.add_subplot(111)
        self.subplot[0].plot(x, y, ptitle)
        self.subplot[0].set_title(ptitle)

      self.f.canvas.mpl_connect('motion_notify_event', self.MouseMotion)
      self.f.canvas.mpl_connect('button_press_event',self.start_corner)
      self.f.canvas.mpl_connect('button_release_event',self.end_corner)

  # Mouse controls 
  def start_corner(self,event):
      if event.xdata != None and event.ydata != None:
          if event.button  == 1:
              self.act_plot = self.f.axes.index(event.inaxes)
              self.corner1 = [event.xdata, event.ydata]
              wid = 0
              hei = 0
              self.rect = patches.Rectangle(self.corner1,wid,hei,alpha=0.2) 
              self.subplot[self.act_plot].add_patch(self.rect)
              self.f.canvas.draw()
          if event.button == 3:
              self.refpoint = [event.xdata, event.ydata]

  def end_corner(self,event):
    if event.button == 1:
        if event.xdata != None and event.ydata != None:
            self.corner2 = [event.xdata, event.ydata]
            if self.f.axes.index(event.inaxes) == self.act_plot:
                xlim = sort([self.corner2[0],self.corner1[0]])
                ylim = sort([self.corner2[1],self.corner1[1]])
                self.subplot[self.act_plot].set_xlim(xlim)
                self.subplot[self.act_plot].set_ylim(ylim)
        self.rect.remove()
        self.f.canvas.draw()
        self.act_plot = None

  def MouseMotion(self,event):
    if event.xdata != None:
        x='%6g' %event.xdata
        self.ShowCoor_x.config(text=x)
    if event.ydata != None:
        y='%6g' %event.ydata
        self.ShowCoor_y.config(text=y)

    if event.button == 1 and event.xdata != None and event.ydata != None:
        if self.act_plot == None:
            # pushed mouse key outside plot, there init function first
            self.start_corner(event)
        self.corner2 = [event.xdata, event.ydata]
        if self.f.axes.index(event.inaxes) == self.act_plot:
            wid = self.corner2[0]-self.corner1[0]
            hei = self.corner2[1]-self.corner1[1]
            self.rect.set_width(wid)
            self.rect.set_height(hei)
            self.f.canvas.draw()
    if event.button == 3 and event.xdata != None and event.ydata != None:
        if self.refpoint == None:
            self.refpoint = [event.xdata, event.ydata]
        self.newpoint = [event.xdata, event.ydata]
        xmove = self.newpoint[0]-self.refpoint[0]
        ymove = self.newpoint[1]-self.refpoint[1]
        act_plot = self.f.axes.index(event.inaxes)
        new_xlim = self.subplot[act_plot].get_xlim()-xmove
        new_ylim = self.subplot[act_plot].get_ylim()-ymove
        self.subplot[act_plot].set_xlim(new_xlim)
        self.subplot[act_plot].set_ylim(new_ylim)

        self.f.canvas.draw()
        
  def autoscale(self,event=None):
    """
    Rescale plot to auto range
    """
    for subplots in self.subplot:
        subplots.autoscale_view()
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


class imagePlot(common_plot):
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
      self.subplot[0].clear()
      self.subplot[0].plot(t, pixval, 'b-')
      self.plotcanvas.show()


class imagePlot2(common_plot):
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

      self.subplot[0].clear()
      self.subplot[1].clear()
      self.subplot[0].plot(xbins, yvalues, 'b-')
      self.subplot[1].plot(ybins, xvalues, 'b-')
      self.plotcanvas.show()

