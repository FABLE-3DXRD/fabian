#! /usr/bin/env python
"""

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:henning.sorensen@risoe.dk
"""
from Tkinter import *
import Pmw
import Image, ImageTk, ImageFile, ImageStat
from tkFileDialog import *
import tkFont
import re,os,sys,time,thread
import math
from numpy import float32

#local fabian imports
from Fabian import insert_peaks
from Fabian import About, Shortcuts
from Fabian import Error
from Fabian.ReliefPlot import ReliefPlot
from Fabian.detector import image_flipping

imageplot_state='normal'
try:
  from Fabian.ImagePlot import imagePlot, imagePlot2
except:
  imageplot_state='disabled'


# fabio imports
import fabio 
from fabio import openimage

colour={'transientaoi' :'RoyalBlue',
        'Zoom'         :'red',
        'Relief'       :'LimeGreen',
        'Rocker'       :'LightBlue',
        'transientline':'red',
        'IntProfile'   :'RoyalBlue', 
        'LineProfile'  :'RoyalBlue',
        'peak_colour'  :'red'}

      
class imageWin:
  globals()["peaks"] = {}
  def __init__(self,master,filename=None,filenumber=0,title=None,
               zoomfactor=1,scaled_min=None,scaled_max=None,
               scale=None,orientation=[1,0,0,1],
               mainwin='no',zoomable='yes',coords=[0,0,0,0],
               image=None,tool=None,showpeaks=None):
    #initialize var
    self.master=master
    #these keep track of the AOIs
    self.aoi=[]
    self.zoom_win = 0
    self.line_win = 0
    self.intprof_win = 0
    self.offset=0
    self.transientaoi=None
    self.transientline=None
    self.maxval=StringVar()
    self.minval=StringVar()
    self.showpeaks = showpeaks
    self.ShowPeaks = BooleanVar()
    self.ShowPeaks.set(showpeaks)
    self.orientation = orientation
    self.peakfilename=None
    if scaled_min: self.minval.set(scaled_min)
    if scaled_max: self.maxval.set(scaled_max)
    if scale:
      self.scale = scale
    else:
      self.scale = 0
    self.tool =tool
    #initialize drawing function to draw the correct object 
    #draw2 points to a drawing function
    if 'Line' in tool:
      self.draw2=self.drawLine
    else:
      self.draw2=self.drawAoi
    master.bind('<F1>',self.updatebindings)
    master.bind('<F2>',self.updatebindings)
    master.bind('<F3>',self.updatebindings)
    master.bind('<F4>',self.updatebindings)
    master.bind('<F5>',self.updatebindings)
    master.bind('C',self.quit_children)
    master.bind('q',self.quit)
    master.bind('p',self.show_peaks)
    master.bind('<FocusIn>',self.MouseEntry)
    master.bind('z',self.rezoom)
    master.bind('x',self.rezoom)
   
    if title: self.master.title(title)
    if filename: self.filename = filename
    
    self.zoomfactor=zoomfactor
    if coords[0]>coords[2]:
      coords[0:3:2]=[coords[2],coords[0]]
    if coords[1]>coords[3]:
      coords[1:4:2]=[coords[3],coords[1]]
     
    self.zoomarea=coords
    #display image and reset scale if scaling is not given
    self.im=image
    self.xsize=abs(coords[2]-coords[0])
    self.ysize=abs(coords[3]-coords[1])
    
    frame = Frame(master, bd=0, bg="white")
    frame.pack()

    #display the images
    self.make_image_canvas(frame)
  
    #make the filename zoom, coordinate, and intensity displays    
    self.make_status_bar(frame)
    
    #run update to set scalings and actually display the images
    #change this to draw/redraw set of functions at some point?
    self.update()
    

  def make_image_canvas(self,container):
    #make imagecanvas
    self.canvas_xsize = int(abs(self.zoomarea[2]-self.zoomarea[0])*self.zoomfactor)
    self.canvas_ysize = int(abs(self.zoomarea[3]-self.zoomarea[1])*self.zoomfactor)
    self.frameImage = Frame(container)
    self.canvas = Canvas(self.frameImage,
                         width=self.canvas_xsize, 
                         height=self.canvas_ysize,
                         bg='black')
    self.canvas.pack(side=TOP,anchor='center', expand=1, fill=X)
    self.frameImage.pack(side=TOP,expand=1)
    #bind events
    self.canvas.bind('<Button-1>', self.Mouse1Press)
    self.canvas.bind('<Button1-Motion>', self.Mouse1PressMotion)
    self.canvas.bind('<Button1-ButtonRelease>', self.Mouse1Release)
    self.canvas.bind('<Motion>', self.MouseMotion)
    self.canvas.bind('<Button-2>', self.Mouse2Press)
    #bind button 3 - the force the zoom tool
    self.canvas.bind('<Button-3>', self.Mouse3Press)
    self.canvas.bind('<Button3-Motion>', self.Mouse3PressMotion)
    self.canvas.bind('<Button3-ButtonRelease>', self.Mouse3Release)
    #bind scroll to rezoom tool
    self.canvas.bind('<Button-4>', self.rezoom)
    self.canvas.bind('<Button-5>', self.rezoom)

  def centerImg(self):
    left, right = self.frameScroll.xview()
    top, bottom = self.frameScroll.yview()
    sizex = right - left
    sizey = bottom - top
    self.frameScroll.xview('moveto',  0.5 - sizex / 2.)
    self.frameScroll.yview('moveto',  0.5 - sizey / 2.)

  def rezoom(self,e=None):
    if e.keysym=='z' or e.num == 4:
      newzoomfactor=self.zoomfactor*2
    elif e.keysym=='x' or e.num == 5:
      newzoomfactor=self.zoomfactor/2.
    self.canvas_xsize = int(abs(self.zoomarea[2]-self.zoomarea[0])*newzoomfactor)
    self.canvas_ysize = int(abs(self.zoomarea[3]-self.zoomarea[1])*newzoomfactor)
    self.canvas.config(width=self.canvas_xsize, height=self.canvas_ysize)
    self.canvas.scale('all',0,0,newzoomfactor/self.zoomfactor,newzoomfactor/self.zoomfactor)
    self.zoomfactor=newzoomfactor
    self.ShowZoom.config(text="%3d %%" %(newzoomfactor*100))
    self.update(newimage=self.im)
    if not 'zoom' in self.master.wm_title(): # If zooming in appWin center the
      self.centerImg()                       # image in the Scrolled frame 
 
  def make_status_bar(self,container):
    frameInfo = Frame(container, bd=0)
    frameInfo.pack(side=BOTTOM,fill=X)
    self.ShowMin = Label(frameInfo, text="Min -1",
                         bg ='white',bd=1, relief=SUNKEN, anchor=W)
    self.ShowMin.pack(side=LEFT)
    self.ShowMax = Label(frameInfo, text="Max -1" ,
                         bg ='white',bd=1, relief=SUNKEN, anchor=W)
    self.ShowMax.pack(side=LEFT)
    self.ShowMean = Label(frameInfo, text="Mean -1",
                          bg ='white',bd=1, relief=SUNKEN, anchor=W)
    self.ShowMean.pack(side=LEFT)
    self.ShowInt = Label(frameInfo, text='    0', 
                         width=12, bg='white', bd=1, relief=RIDGE, anchor=W)
    self.ShowInt.pack(side=RIGHT, padx=2)
    self.ShowCoor = Label(frameInfo, text='    0,    0', width =10, 
                          bg ='white',bd=1, relief=RIDGE, anchor=W)
    self.ShowCoor.pack(side=RIGHT, padx = 2)
    self.ShowZoom = Label(frameInfo, text="%3d %%" %(self.zoomfactor*100), 
                          width =6, bg ='white',bd=1, relief=RIDGE, anchor=W)
    self.ShowZoom.pack(side=RIGHT, padx = 2)


  def show_peaks(self,event=None):
    # Using <p> to toggle between show and don't show peaks 

    #print 'IN SHOW_PEAKS',self.master.title(),self.showpeaks
    if event !=None:
      if event.keysym == 'p':
        if self.showpeaks == False:
          self.showpeaks = True
          self.ShowPeaks.set(True)
        else:
          self.showpeaks = False
          self.ShowPeaks.set(False)
    self.master.config(cursor='watch') 
    # The next two lines is a hack to have the configure done imidiately
    self.canvas.create_oval((0,0,0,0),tag='hack',outline='red')
    self.canvas.delete('hack')

    try:
      self.showpeaks = self.ShowPeaks.get()
    except:
      pass

    if self.showpeaks == False:     # Remove peaks from canvas  
      self.clear_peaks()
      self.master.config(cursor='left_ptr')
      return
    elif peaks == {} :# or self.newpeaks == True:   # If empty peak database
      if self.read_peaks() == False: # Read peaks, 
                                     #but if no peak file is given 
                                     # reset variables and return
        self.master.config(cursor='left_ptr') 
        if self.newpeaks == True:
          self.newpeaks = False
        else:
          self.showpeaks = False
          self.ShowPeaks.set(False)
        return
    from xfab.detector import xy_to_detyz


      
    try: # draw peaks on canvas
      self.canvas.delete('peaks')
      #myc = 0
      for ipeaks in peaks[os.path.split(self.filename.get())[-1]]:
        #myc += 1
        if int(ipeaks[0]) > globals()["min_pixel"]:
          # The -1 in front of o11,o12 etc is accomodate for
          # Rot180 made on the screen
          (xp, yp) = xy_to_detyz([ipeaks[2],ipeaks[1]],
                                 -1*self.orientation[0],
                                 -1*self.orientation[1],
                                 -1*self.orientation[2],
                                 -1*self.orientation[3],
                                 globals()["image_xsize"],
                                 globals()["image_ysize"])

          #if myc < 10: 
          #  print [ipeaks[1],ipeaks[2]],[xp,yp]
          circ_center=[(xp-self.zoomarea[0])*self.zoomfactor,
                       (yp-self.zoomarea[1])*self.zoomfactor]
          rad = globals()["peak_radius"]*self.zoomfactor
          corners=(circ_center[0]-rad,circ_center[1]-rad,
                   circ_center[0]+rad,circ_center[1]+rad)
          self.canvas.create_oval(corners,tag='peaks',outline=colour['peak_colour'])
    except: # no peaks for the present image was found in the peaks database
      try:
        self.ErrorInfo.config(text='No peaks for this image', bg='red')
        self.master.config(cursor='left_ptr')
        #self.ShowPeaks.set(False)
        #self.showpeaks = False
      except:
        pass

    # Reset parameters
    self.master.config(cursor='left_ptr')
    self.newpeaks = False
    return

  def read_newpeaks(self,event=None):
    self.read_peaks()
    self.ShowPeaks.set(True)
    self.showpeaks = True
    self.show_peaks()
    
      
  def read_peaks(self):
    rpeaks = insert_peaks.readpeaksearch()
    self.peakfilename = askopenfilename(filetypes=[("spt files", "*.spt"),("All Files", "*")])
    if len(self.peakfilename) == 0:
        return False
    rpeaks.readallpeaks(self.peakfilename)
    peaks = rpeaks.images
    ks = [ os.path.split(name)[-1] for name in peaks.keys() ]
    # convert coordinates to "fabian" coordinates
    for k in ks:
      for i in range(len(peaks[k])):
        mx = float(peaks[k][i][2])
        #my = image_ysize-float(peaks[k][i][1])
        my = float(peaks[k][i][1])
        peaks[k][i][0] = int(peaks[k][i][0])
        peaks[k][i][1] = mx
        peaks[k][i][2] = my
    globals()["peaks"] = peaks
    return

  def clear_peaks(self,event=None):
    self.showpeaks = False
#    self.ShowPeaks.set(self.showpeaks)
    self.canvas.delete('peaks')


  def update_peaks(self,event=None):
    self.canvas.delete('peaks')
    #globals()["min_pixel"] = self.min_pixel.get()
    #globals()["peak_radius"] = self.peak_radius.get()
    #colour['peak_colour'] = self.peak_colour.get()
    self.show_peaks()


  def MouseMotion(self,event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasx(event.y)
    if x<self.canvas_xsize and y<self.canvas_ysize:
      xy =  "%5i,%5i"%(x/self.zoomfactor +self.zoomarea[0],
                       y/self.zoomfactor +self.zoomarea[1])
      self.xsize = globals()["image_xsize"]
      self.ysize = globals()["image_ysize"]
#      xy =  "%5i,%5i"%(self.xsize-1-(x/self.zoomfactor +self.zoomarea[0]),
#                       self.ysize-1-(y/self.zoomfactor +self.zoomarea[1]))
      xy =  "%5i,%5i"%(self.xsize-1-math.floor(x/self.zoomfactor +self.zoomarea[0]),
                       self.ysize-1-math.floor(y/self.zoomfactor +self.zoomarea[1]))
      self.ShowCoor.config(text=xy)
      I = " %10g"% self.im.getpixel((x/self.zoomfactor +self.zoomarea[0],
                                     y/self.zoomfactor +self.zoomarea[1]))
      self.ShowInt.config(text=I)
 
  def Mouse2Press(self, event):
    self.canvas.delete()
    y=self.canvas.canvasx(event.y)
    
  def Mouse3Press(self, event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasy(event.y)
    x,y=self.val_canvas_coord((x,y))
    self.transientcorners=[x,y,x,y]

  def Mouse3PressMotion(self, event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasy(event.y)
    x,y=self.val_canvas_coord((x,y))
    self.transientcorners[2:]=[x,y]
    self.drawAoi()
    self.MouseMotion(event)
  def Mouse3Release(self, event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasy(event.y)
    x,y=self.val_canvas_coord((x,y))
    self.transientcorners[2:]=[x,y]
    #save whichever tool was active
    tmp=self.draw2
    self.draw2=self.drawAoi
    self.use_tool(tool='Zoom')
    self.draw2=tmp
    
  def Mouse1Press(self, event):
    self.master.focus_set()
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasy(event.y)
    x,y=self.val_canvas_coord((x,y))
    self.transientcorners=[x,y,x,y]
  def Mouse1PressMotion(self, event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasy(event.y)
    x,y=self.val_canvas_coord((x,y))
    self.transientcorners[2:]=[x,y]
    self.draw2()
    self.MouseMotion(event)
  def Mouse1Release(self, event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasy(event.y)
    x,y=self.val_canvas_coord((x,y))
    self.transientcorners[2:]=[x,y]
    self.use_tool()
    #self.draw(tool=self.tool)
  
  def MouseEntry(self,event):
    #mouse has entered the window - check for nonexistent children
    children=self.master.winfo_children()
    removechild = []
    for w in self.aoi:
      if not w['zoomwin'].master in children:
	for l in w['aoi']:
          self.canvas.delete(l)
        removechild.append(w)
    for w in removechild:
      self.aoi.remove(w)
  
  def val_canvas_coord(self,c):
    c_new=[c[0],c[1]]
    if c[0]<0:
      c_new[0]=0
    elif c[0]>self.canvas_xsize:
      c_new[0]=self.canvas_xsize
    if c[1]<0:
      c_new[1]=0
    elif c[1]>self.canvas_ysize:
      c_new[1]=self.canvas_ysize
    return c_new
    
  def use_tool(self,tool=None):
    if not tool:
      tool=self.tool
    # Convert canvas coordinates into pixels
    t=self.transientcorners
    corners=[int(self.zoomarea[0]+t[0]/self.zoomfactor), 
             int(self.zoomarea[1]+t[1]/self.zoomfactor),
             int(self.zoomarea[0]+t[2]/self.zoomfactor),
             int(self.zoomarea[1]+t[3]/self.zoomfactor)]

    if 'Relief' in tool:
        if corners[0]==corners[2] or corners[1]==corners[3]:
          self.canvas.delete('transientaoi')
          return
	if 'zoom' in self.master.wm_title():
          t= 'relief of ' + self.master.wm_title()
        else:
          t='relief of main'
	opensubwin=self.openrelief
    elif 'Zoom' in tool:
        if corners[0]==corners[2] or corners[1]==corners[3]:
          self.canvas.delete('transientaoi')
          return
        if 'zoom' in self.master.wm_title():
          t= self.master.wm_title() +'.%d' %  self.zoom_win
        else:
          t='zoom %d' % self.zoom_win
        opensubwin=self.openzoom
        self.zoom_win=self.zoom_win+1
    elif 'IntProfile' in tool:
        if corners[0]==corners[2] or corners[1]==corners[3]:
          self.canvas.delete('transientaoi')
          return
        if 'zoom' in self.master.wm_title():
          t= 'Integrated profile %d of ' \
              %self.intprof_win + self.master.wm_title()
          self.intprof_win = self.intprof_win + 1
        else:
          t='Integrated profile %d' % self.intprof_win
          self.intprof_win = self.intprof_win + 1
        opensubwin=self.openintprofile
    elif 'Rock' in tool:
	t = 'rock'
	opensubwin=self.openrocker
    elif 'Line' in tool:
      if corners[:2]==corners[2:]:
        self.canvas.delete('transientline')
        return
      if 'zoom' in self.master.wm_title():
        t= self.master.wm_title() +'.%d' %  self.line_win
        self.line_win = self.line_win + 1
      else:
        t='Line %d of main' % self.line_win
        self.line_win = self.line_win + 1
      opensubwin=self.openlineprofile

    self.aoi.append({'coords':self.transientcorners,
                     'aoi':[self.draw2(tool=tool)],
                     'zoomwin': opensubwin(t),
                     'wintype':tool})

  def drawAoi(self,tool='transientaoi'):
    self.canvas.delete('transientaoi')
    return self.canvas.create_rectangle(self.transientcorners,tag=tool,outline=colour[tool])

  def drawLine(self,tool='transientline'):
    self.canvas.delete('transientline')
    t_end=4
    tc=self.transientcorners
    #calc the end section coordinates
    endsec = ([tc[2]-tc[0], tc[3]-tc[1]])
    normendsec = math.sqrt(endsec[0]*endsec[0]+endsec[1]*endsec[1])
    if normendsec == 0:
      #line has no length - i.e. no line should be drawn and no plot should be opened (no?)
      return
    else:
      endsec[0] = endsec[0]/normendsec*t_end
      endsec[1] = endsec[1]/normendsec*t_end
      #line is drawn as a polyline in one single object
      line=(tc[0]-endsec[1],tc[1]+endsec[0],tc[0]+endsec[1],tc[1]-endsec[0],
            tc[0],tc[1],tc[2],tc[3],
            tc[2]-endsec[1],tc[3]+endsec[0],tc[2]+endsec[1],tc[3]-endsec[0])
    return self.canvas.create_line(line,tag=tool,fill=colour[tool])

 
  def openzoom(self,tag):
    t=self.transientcorners
    corners=[int(self.zoomarea[0]+t[0]/self.zoomfactor),
             int(self.zoomarea[1]+t[1]/self.zoomfactor),
             int(self.zoomarea[0]+t[2]/self.zoomfactor),
             int(self.zoomarea[1]+t[3]/self.zoomfactor)]
    w=Toplevel(self.master)
    if self.tool:
      newwin=imageWin(w,
                      title=tag,
                      filename=self.filename,
                      zoomfactor=self.zoomfactor*4,
                      scaled_min=self.minval.get(),
                      scaled_max=self.maxval.get(),
                      scale=self.scale,coords=corners,
                      image=self.im,
                      orientation=self.orientation,
                      tool=self.tool,
                      showpeaks=self.showpeaks)
      newwin.tool=self.tool
    else:
      newwin=imageWin(w,
                      title=tag,
                      filename=self.filename,
                      zoomfactor=self.zoomfactor*4,
                      coords=corners,
                      orientation=self.orientation,
                      image=self.im,
                      tool=None)
    return newwin

  def openintprofile(self,tag):
    t=self.transientcorners
    # Make sure smallest pixel value is first
    if t[0] > t[2]:
      tmp = t[0]
      t[0] = t[2]
      t[2] = tmp
    if t[1] > t[3]:
      tmp = t[1]
      t[1] = t[3]
      t[3] = tmp
    corners=[int(self.zoomarea[0]+t[0]/self.zoomfactor),
             int(self.zoomarea[1]+t[1]/self.zoomfactor),
             int(self.zoomarea[0]+t[2]/self.zoomfactor),
             int(self.zoomarea[1]+t[3]/self.zoomfactor)]
    w=Toplevel(self.master)
    
    xbins = []
    ybins = []
    xvalues = []
    yvalues = []
    for x in range(corners[0],corners[2]):
      y_int = 0
      xbins.append(x)
      for y in range(corners[1],corners[3]):
        y_int = y_int + self.im.getpixel((x,y))
      yvalues.append(y_int)

    for y in range(corners[1],corners[3]):
      x_int = 0
      ybins.append(y)
      for x in range(corners[0],corners[2]):
        x_int = x_int + self.im.getpixel((x,y))
      xvalues.append(x_int)
      
    linewin = imagePlot2(w,
                         title=tag,
                         x=xbins,
                         y=yvalues,
                         ptitle='Horizontal',
                         x2=ybins,
                         y2=xvalues,
                         ptitle2='Vertical')
    linewin.zoomarea = corners
    return linewin



  def openlineprofile(self,tag):
      # Make lineprofile  relief window
      t=self.transientcorners
      corners=[(self.zoomarea[0]+t[0]/self.zoomfactor),
               (self.zoomarea[1]+t[1]/self.zoomfactor),
               (self.zoomarea[0]+t[2]/self.zoomfactor-1),
               (self.zoomarea[1]+t[3]/self.zoomfactor)-1]
      from Fabian import pixel_trace
      w=Toplevel(self.master)
      pixels = pixel_trace.pixel_trace(corners)
      t = []
      pixval = []
      path = 0
      for i in range(len(pixels)):
        path = path + pixels[i][2]
        t.append(i)
        pixval.append(self.im.getpixel((pixels[i][0],pixels[i][1])))
      linewin = imagePlot(w,title=tag,x=t,y=pixval)
      linewin.zoomarea = corners
      return linewin
    
  def openrelief(self,tag):
      # Make 3D relief window
      t=self.transientcorners
      # Make sure smallest pixel value is first
      if t[0] > t[2]:
        tmp = t[0]
        t[0] = t[2]
        t[2] = tmp
      if t[1] > t[3]:
        tmp = t[1]
        t[1] = t[3]
        t[3] = tmp

      corners=[int(self.zoomarea[0]+t[0]/self.zoomfactor),
               int(self.zoomarea[1]+t[1]/self.zoomfactor),
               int(self.zoomarea[0]+t[2]/self.zoomfactor),
               int(self.zoomarea[1]+t[3]/self.zoomfactor)]
      
      reli=Toplevel(self.master)
      reli.title(tag)
      newReli=ReliefPlot(reli,newimage=self.im,corners=corners)
      newReli.zoomarea = corners

      return newReli

  def openrocker(self,tag):
      t=self.transientcorners
      # Make sure smallest pixel value is first
      if t[0] > t[2]:
        tmp = t[0]
        t[0] = t[2]
        t[2] = tmp
      if t[1] > t[3]:
        tmp = t[1]
        t[1] = t[3]
        t[3] = tmp
      self.corners=[int(self.zoomarea[0]+t[0]/self.zoomfactor),
                    int(self.zoomarea[1]+t[1]/self.zoomfactor),
                    int(self.zoomarea[0]+t[2]/self.zoomfactor),
                    int(self.zoomarea[1]+t[3]/self.zoomfactor)]
      # change here for change to deconstruct
      self.center = fabio.extract_filenumber(self.filename.get())
      defdelta = 1
      rockerpar=Toplevel(self.master)
      rockerpar.title('Rocking curve setup')
      frame = Frame(rockerpar, bd=0, bg="white") #, width=600, height=600) 
      frame.pack()
      self.seriestype = StringVar()
      self.seriestype.set('delta')
      self.delta = IntVar()
      self.startframe = IntVar()
      self.endframe = IntVar()
      self.delta.set(defdelta)
      self.startframe.set(self.center-defdelta)
      self.endframe.set(self.center+defdelta)
      radio1 = Frame(frame)
      Radiobutton(radio1,
                  text='Rocking curve +/- ', 
                  variable=self.seriestype, 
                  value='delta',anchor=W).pack(side=LEFT,fill=BOTH)
      e=Entry(radio1, textvariable=self.delta, bg='white', width=6)
      e.bind('<FocusIn>',self.setradio1)
      e.pack(side=LEFT)
      Label(radio1, text="frames").pack(side=LEFT)
      radio1.pack(fill=BOTH)
      radio2 = Frame(frame)
      Radiobutton(frame,
                  text='Rocking curve from frame', 
                  variable=self.seriestype, 
                  value='startend',anchor=W).pack(side=LEFT,fill=BOTH)
      e=Entry(radio2, textvariable=self.startframe, bg='white', width=6)
      e.bind('<FocusIn>',self.setradio2)
      e.pack(side=LEFT)
      Label(radio2, text="to").pack(side=LEFT)
      e=Entry(radio2, textvariable=self.endframe, bg='white', width=6)
      e.bind('<FocusIn>',self.setradio2)
      e.pack(side=LEFT)
      radio2.pack()
      Button(rockerpar, text='Go rock', command=self.GoRock).pack(side=BOTTOM)
      return frame
      
  def GoRock(self):
    if self.seriestype.get() == 'startend':
      startframe = self.startframe.get()
      endframe = self.endframe.get()
    else:
      startframe = self.center-self.delta.get()
      endframe = self.center+self.delta.get()
      self.startframe.set(startframe)
      self.endframe.set(endframe)
    from Fabian import rocker
    rockdata = rocker.rocker(filename_sample=self.filename.get(),
                             coord=self.corners,
                             startnumber=startframe,
                             endnumber=endframe)
    rockdata.run()
    w=Toplevel(self.master)
    linewin = imagePlot(w,title='Rocking curve',x=rockdata.imagenumber,y=rockdata.getdata())
    return linewin
  
  def setradio1(self,event=None):     # Sets the radiobuttom to make fileseries from
      self.seriestype.set('delta')    #  -x to +x images from current

  def setradio2(self,event=None):     # Sets the radiobuttom to make fileseries
      self.seriestype.set('startend') # from No.X to No Y.

  def get_img_stats(self, image):
    #this is a hack _while thinking of a better solution
    imin,imax=image.getextrema()
    l=list(image.getdata())
    imean=sum(l)/len(l)
    return (imin,imax,imean)
   
  def update(self,scaled_min=0,scaled_max=0,
             newimage=None,
             filename=None,
             orientation=None,
             showpeaks=False):
    if  orientation != None:
      self.orientation = orientation

    if self.scale==0:
      self.reset_scale()
    if (scaled_min==scaled_max==0):
      scaled_min = float(self.minval.get())
      scaled_max = float(self.maxval.get())
    else:
      self.minval.set(scaled_min)
      self.maxval.set(scaled_max)
    if (scaled_max-scaled_min) < 10**(-6): # set scale to zero if min=max 
      self.scale = 0.0
    else:
      self.scale = 255.0 / (scaled_max - scaled_min)
    self.offset = - scaled_min * self.scale
    if newimage: 
      self.im=newimage
    imcrop = self.im.crop(self.zoomarea)
    im8c = imcrop.point(lambda i: i * self.scale + self.offset).convert('L')
    ###>
#    self.canvas_xsize = int(abs(self.zoomarea[2]-self.zoomarea[0])*self.zoomfactor)
#    self.canvas_ysize = int(abs(self.zoomarea[3]-self.zoomarea[1])*self.zoomfactor)
    ###<
    self.img = ImageTk.PhotoImage(im8c.resize((self.canvas_xsize,self.canvas_ysize)))
    self.im_min,self.im_max,self.im_mean = self.get_img_stats(imcrop)
    self.ShowMin.config(text="Min %10g" %(self.im_min))
    self.ShowMax.config(text="Max %10g" %(self.im_max))
    self.ShowMean.config(text="Mean %10g" %(self.im_mean))
    self.canvas.lower(self.canvas.create_image(0,0,anchor=NW, image=self.img))

    try:
      showpeaks = self.ShowPeaks.get()
    except:
      showpeaks = self.showpeaks

    #print 'HHH peaks', self.master.title(), showpeaks

    if showpeaks == True:
      self.update_peaks()
      
    #print 'HHH', self.master.title(), self.orientation
    #update children
    for w in self.aoi:
      # Firstly check if object is inside image area
      if w['zoomwin'].zoomarea[2]>self.zoomarea[2] or  \
            w['zoomwin'].zoomarea[3]>self.zoomarea[3]:
        w['zoomwin'].quit()
        continue
      # If so update obj.
      if w['wintype'] in ('Zoom'):
        w['zoomwin'].update(scaled_min,
                            scaled_max,
                            newimage=self.im,
                            orientation=self.orientation,
                            showpeaks=showpeaks)
      if w['wintype'] in ('IntProfile'):
        w['zoomwin'].update(coord=w['coords'],
                            zoomarea=self.zoomarea,
                            zoomfactor=self.zoomfactor,
                            newimage=self.im)
      if w['wintype'] in ('LineProfile'):
        w['zoomwin'].update(coord=w['coords'],
                            zoomarea=self.zoomarea,
                            zoomfactor=self.zoomfactor,
                            newimage=self.im)
      if w['wintype'] in ('Relief'):
        w['zoomwin'].update(newimage=self.im)
      #check for invalid aois, i.e. remove those outside an image
    return True
  
  def reset_scale(self):
    #find best image grayscale for the present image.
    #only to be called when this is the main window instance
    self.im_min,self.im_max = self.im.getextrema()
    

    #Autoscaling image
    hist = self.im.histogram()
    sumhist = sum(hist)

    ilow = -1
    cc = 0
    while cc < 0.01*sumhist:
      ilow = ilow + 1
      cc = cc + hist[ilow]

    cc= 0
    ihigh = 255
    while cc < 0.01*sumhist:
      ihigh = ihigh - 1
      cc = cc + hist[ihigh]
      
    if ilow==ihigh: ihigh = ihigh +1
    scaled_min = (self.im_max - self.im_min)/255 *ilow +self.im_min
    scaled_max = (self.im_max - self.im_min)/255 *ihigh +self.im_min
    self.minval.set("%f"%scaled_min)
    self.maxval.set("%f"%scaled_max)
    
  def setbindings(self):
    try:
      self.tool = self.ToolType.get()
    except:
      pass
    if 'LineProfile' in self.tool:
      self.draw2=self.drawLine
    else:
      self.draw2=self.drawAoi
    #update children
    for w in self.aoi:
      if w['wintype']=='Zoom':
	w['zoomwin'].tool=self.tool
	w['zoomwin'].setbindings()

  def updatebindings(self,event=None,tool=None):
    if event.keysym=='F1':
      try:
        self.ToolType.set('Zoom')
      except:
        self.tool = 'Zoom'
      self.setbindings()
    if event.keysym=='F2' and imageplot_state!='disabled':
      try:
        self.ToolType.set('LineProfile')
      except:
        self.tool='LineProfile'
      self.setbindings()
    if event.keysym=='F3' and imageplot_state!='disabled':
      try:
        self.ToolType.set('IntProfile')
      except:
        self.tool='IntProfile'
      self.setbindings()
    if event.keysym=='F4':
      try:
        self.ToolType.set('Relief')
      except:
        self.tool='Relief'
      self.setbindings()
    if event.keysym=='F5' and imageplot_state!='disabled':
      try:
        self.ToolType.set('Rocker')
      except:
        self.tool='Rocker'
      self.setbindings()

  def quit_children(self,event=None):
    #update children
    for w in self.aoi:
      # Firstly check if object is inside image area
      w['zoomwin'].quit()
    self.MouseEntry(None)
    return True


  def quit(self,event=None):
    self.master.destroy()

class appWin(imageWin):
  def __init__(self,
               master,
               filenumber=0,
               filename=None,
               filetype=None,
               zoomfactor=1,
               mainwin='no',
               zoomable='yes',
               coords=[0,0,0,0],
               image=None):
    #initialize var
    self.master=master
    #these keep track of the AOIs
    self.aoi=[]
    self.orientation = [1,0,0,1]
    self.zoom_win = 0
    self.line_win = 0
    self.intprof_win = 0
    self.scale=0
    self.offset=0
    self.transientaoi=None
    self.transientline=None
    self.maxval=StringVar()
    self.minval=StringVar()
    self.scaled_min=0
    self.scaled_max=0
    self.displaynumber=StringVar()
    self.filename=StringVar()
    self.ToolType = StringVar()
    self.tool = 'Zoom' # Set default event of mouse bottom 1 to Zoom
    self.histfile = StringVar()
    self.histlength = 0
    self.HistMenuItems = []

    self.peak_colour = StringVar()
    self.peak_colour.set("blue")
    self.peak_radius = IntVar()
    self.peak_radius.set(8)
    self.newpeaks = False
    self.FlipHorz = BooleanVar()
    self.FlipHorz.set(False)
    self.FlipVert = BooleanVar()
    self.FlipVert.set(False)
    self.Rot90 = BooleanVar()
    self.Rot90.set(False)
    self.Rot180 = BooleanVar()
    self.Rot180.set(False)
    self.Rot270 = BooleanVar()
    self.Rot270.set(False)
    self.TransformOrder = []
    self.header_sort_type = StringVar()
    self.header_sort_type.set('original')
    #self.header_sort_type.set('alphabetical')

    globals()["opendir"] = "."
    globals()["min_pixel"] = 4
    globals()["peak_radius"] = 8
    self.min_pixel = IntVar()
    self.min_pixel.set(globals()["min_pixel"])
    self.peak_radius = IntVar()
    self.peak_radius.set(globals()["peak_radius"])
    self.draw2=self.drawAoi
    self.ToolType.set(self.tool)
    self.ShowPeaks = BooleanVar()
    self.showpeaks = False
    self.ShowPeaks.set(False)
    self.ImOrient = IntVar()
    self.ImOrient.set(1)
    self.autofileupdate = BooleanVar()
    self.autofileupdate.set(False)
    self.sleeptime = 0
    self.peaks = {}
    self.BgCorrect = BooleanVar()
    self.BgCorrect.set(False)
    self.FfCorrect = BooleanVar()
    self.FfCorrect.set(False)
    self.bgimage = None
    self.ffimage = None

    master.bind('<F1>',self.updatebindings)
    master.bind('<F2>',self.updatebindings)
    master.bind('<F3>',self.updatebindings)
    master.bind('<F4>',self.updatebindings)
    master.bind('<F5>',self.updatebindings)
    master.bind('o',self.OpenFile)
    master.bind('C',self.quit_children)
    master.bind('q',self.quit)
    master.bind('a',self.about)
    master.bind('h',self.help)
    master.bind('<FocusIn>',self.MouseEntry)
    master.bind('z',self.rezoom)
    master.bind('x',self.rezoom)
    master.bind('c',self.clear_peaks)
    master.bind('p',self.show_peaks)
    master.bind('r',self.read_newpeaks)
    master.bind('f',self.autonextimage)
    master.bind('<Up>',self.updatetime)
    master.bind('<Down>',self.updatetime)
    master.bind('<Right>',self.nextimage)
    master.bind('<Left>',self.previousimage)

    frame = Frame(master, bd=0, bg="white")
    frame.pack(fill=X)

    #add menubar
    self.make_command_menu(frame)

    if filename:
      self.filename.set(filename)
    else:
      self.OpenFile(filename=None)

    self.zoomfactor=zoomfactor
    #display image and reset scale if scaling is not given
    self.openimage()
    self.displaynumber.set(fabio.getnum(self.filename.get()))
    self.reset_scale()

    self.zoomarea = [0,0,self.xsize,self.ysize]
    #set the image dimensions and zoom out if it is big
    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    self.zoomfactor = min( round(screen_width/(1.*self.xsize)*10)/10,
                           round(screen_height/(2.*self.ysize)*10)/10)
    self.canvas_xsize = int(abs(self.zoomarea[2]-self.zoomarea[0])*\
                              self.zoomfactor)
    self.canvas_ysize = int(abs(self.zoomarea[3]-self.zoomarea[1])*\
                              self.zoomfactor)

    #Add Notebook tabs
    self.noteb1 = Pmw.NoteBook(frame)
    self.noteb1.pack(side=BOTTOM,fill='both')
    self.page1 = self.noteb1.add('Image')
    self.page2 = self.noteb1.add('Info')
    
    #call __init__ in the parent class
    self.make_scaling_ctls(self.page1)
    self.frameScroll = Pmw.ScrolledFrame(self.page1, 
                                         hull_width=self.canvas_xsize+30, 
                                         hull_height=self.canvas_ysize+30,
                                         usehullsize=1,
                                         hscrollmode='static',
                                         vscrollmode='static')
    self.frameScroll.pack()
    self.make_image_canvas(self.frameScroll.interior())
    
    self.make_header_info()
    self.make_status_bar(self.page1)
    self.noteb1.setnaturalsize()
    
    # Put header on page2 Info
    hc = Pmw.Group(self.page2,tag_text='Order of header items')
    hc.pack(fill=BOTH,side=TOP,anchor=W)


    r=Radiobutton(hc.interior(),
                  text='Original',
                  command=(lambda:self.update_header_page(True)),
                  variable=self.header_sort_type,
                  value='original',
                  anchor=W,
                  width=20).pack(side=LEFT,anchor=W)
    r=Radiobutton(hc.interior(),
                  text='Alphabetical',
                  command=(lambda:self.update_header_page(True)),
                  variable=self.header_sort_type,
                  value='alphabetical',
                  anchor=W,
                  width=20).pack(side=LEFT,anchor=W)
    self.HeaderFrame = Pmw.ScrolledFrame(self.page2, labelpos=N)
    self.HeaderFrame.pack(fill=BOTH, expand=YES)
    self.HeaderInterior = self.HeaderFrame.interior()
    self.make_header_page()
    
    #run update to set scalings and actually display the images
    #change this to draw/redraw set of functions at some point?
    self.update()
    self.setbindings()
    self.page1.focus_force() # In Windows the focus seemingly
                             # need to enforced otherwise
                             # the entries can not be edited 
                             # unless one moves focus to a
                             # different window and back 


  def make_header_page(self):
      self.headcheck=[]
      self.headtext={}
      self.newitem={}
      # To choose sorting type 
      if self.header_sort_type.get() == 'original':
        header_sorted = self.im.header.keys()
      elif self.header_sort_type.get() == 'alphabetical':
        header_sorted = self.im.header.keys()
        header_sorted.sort()
      #       
      
      for item in header_sorted:
        fm = Frame(self.HeaderInterior)
        self.newitem[item]=StringVar()
        c=Checkbutton(fm,text='%s' %(item),
                      command=self.update_header_label,
                      variable=self.newitem[item],
                      bg='white',
                      anchor=W,
                      width=20).pack(side=LEFT,anchor=W)
        self.headcheck.append(c)
        self.headtext[item]= Label(fm,
                                   text='%s' %(self.im.header[item]),
                                   bg='white',
                                   anchor=W,
                                   width=100)
        self.headtext[item].pack(side=LEFT,fill=X,expand='yes')
        fm.pack(side=TOP,anchor=W)

  def make_header_info(self):
    
    self.TextInfo = Frame(self.page1, bd=0)
    self.TextInfo.pack(side=TOP,fill=X)

    self.HeaderInfo = Label(self.TextInfo, text='', anchor=W)
    self.HeaderInfo.pack(side=LEFT,fill=BOTH)

    self.ErrorInfo = Label(self.TextInfo, text='',anchor=W)
    self.ErrorInfo.pack(side=RIGHT,fill=BOTH)

#    self.HeaderInfo = Label(self.page1, text='', anchor=W)
#    self.HeaderInfo.pack(side=TOP,fill=BOTH)

#    self.ErrorInfo = Label(self.page1, text='fdfdfd', anchor=W)
#    self.ErrorInfo.pack(side=TOP,fill=BOTH)
    
  def clear_header_page(self):
    for child in self.HeaderInterior.winfo_children():
      child.destroy()

  def update_header_page(self,newsorting=False):
    # check if the set of (possibly newly read from disk) header items
    # is identical to the one displayed
    if newsorting == True:
      self.clear_header_page()
      self.make_header_page()
    else:      
      if set(self.im.header.keys())==set(self.headtext.keys()):
          # they seem to be compatible, note - this
          # keeps the checked checkboxes alive
          for item,value in self.im.header.iteritems():
            self.headtext[item].config(text='%s' % value)
      else:
          # they differ - make a new header page from scratch
          # first remember the checked items to keep them 
          # checked if the exist in the new header
          checkeditems=[]
          for item,value in self.newitem.iteritems():
            if value.get()=='1':
              checkeditems.append(item)
          self.clear_header_page()
          self.make_header_page()
          #recheck the items that are found in the hew header
          for item in checkeditems:
            if item in self.newitem.keys():
              self.newitem[item].set('1')

  def update_header_label(self):
    headertext = ''
    self.newitem.keys().sort()
    keys=self.newitem.keys()
    keys.sort()
    for item in keys:
      if self.newitem[item].get() == '1':
            headertext = headertext+item+': '+'%s' %(self.im.header[item]) +'; '
    self.HeaderInfo.config(text='%s' %(headertext))

  def rebind(self,e): # Hack to unbind the image change 
                      # stuff when focus is in an entry
    if self.master.focus_get() == self.master:
      self.master.bind('<Left>',self.previousimage)
      self.master.bind('<Right>',self.nextimage)
    else:
      self.master.unbind('<Left>')
      self.master.unbind('<Right>')
          
  def make_scaling_ctls(self,master):
    frameScale = Frame(master, bd=0)
    #self.master2 = master
    # Image scale controls  
    Label(frameScale,text='Scale: ').pack(side=LEFT)
    Label(frameScale,text='min:', bg='white').pack(side=LEFT)
    self.emin=Entry(frameScale, textvariable=self.minval, bg='white', width=6)
    self.emin.bind('<Return>',self.rescale)
    self.emin.bind('<FocusIn>', self.rebind)
    self.emin.bind('<FocusOut>',self.rebind)
    self.emin.bind('<KP_Enter>',self.rescale)
    self.emin.pack(side=LEFT,padx=4)
    
    Label(frameScale,text='max:', bg='white').pack(side=LEFT)
    self.emax=Entry(frameScale, textvariable=self.maxval, bg='white', width=6)
    self.emax.bind('<Return>',self.rescale)
    self.emax.bind('<KP_Enter>',self.rescale)
    self.emax.bind('<FocusIn>', self.rebind)
    self.emax.bind('<FocusOut>',self.rebind)
    self.emax.pack(side=LEFT,padx=4)
    Button(frameScale,text='update', 
           bg='white', 
           command=self.update).pack(side=LEFT,padx=2)
    Button(frameScale,text='reset', 
           bg='white', 
           command=self.reset_scale).pack(side=LEFT,padx=2)
    Button(frameScale,text='next',
           bg='white', 
           command=self.nextimage).pack(side=RIGHT)
    Button(frameScale,text='previous', 
           bg='white', 
           command=self.previousimage).pack(side=RIGHT)
    self.efilen=Entry(frameScale, 
                      textvariable=self.displaynumber, 
                      bg='white', 
                      width=6)
    self.efilen.bind('<FocusOut>',self.rebind)
    self.efilen.bind('<FocusIn>',self.rebind)
    self.efilen.bind('<Return>',self.gotoimage)
    self.efilen.bind('<KP_Enter>',self.gotoimage)
    self.efilen.pack(side=RIGHT,padx=8)
    Button(frameScale,
           text='go to number:', 
           bg='white', 
           command=self.gotoimage).pack(side=RIGHT, padx=2)
    frameScale.pack(side=TOP,expand=1, pady=10, fill=X)
     
  def make_command_menu(self,master):
    frameMenubar = Frame(master,relief=RAISED, borderwidth=2)
    
    FileMenu = Menubutton(frameMenubar, text='File',underline=0)
    FileMenu.pack(side=LEFT, padx="2m")
    FileMenu.menu =Menu(FileMenu)
    FileMenu.menu.add_command(label='Open', underline=0, command=self.OpenFile)
    FileMenu.menu.add_checkbutton(label='Auto file update',
                                  command=self.autonextimage,
                                  onvalue=True,
                                  offvalue=False,
                                  variable=self.autofileupdate)
    FileMenu.menu.add_command(label='quit', underline=0, command=self.quit)
    FileMenu['menu']=FileMenu.menu

    ToolMenu = Menubutton(frameMenubar, text='Tools',underline=0)
    ToolMenu.pack(side=LEFT, padx="2m")
    ToolMenu.menu =Menu(ToolMenu)
    ToolMenu.menu.add_radiobutton(label='Zoom%15s%2s' %('','F1'),
                                  command=self.setbindings,
                                  variable=self.ToolType,
                                  value='Zoom')
    ToolMenu.menu.add_radiobutton(label='Line profile%7s%2s' %('','F2') ,
                                  command=self.setbindings,
                                  variable=self.ToolType,
                                  value='LineProfile',state=imageplot_state)
    ToolMenu.menu.add_radiobutton(label='Integr. profile%3s%2s' %('','F3'),
                                  command=self.setbindings,
                                  variable=self.ToolType,
                                  value='IntProfile',state=imageplot_state)
    ToolMenu.menu.add_radiobutton(label='Relief plot%8s%2s' %('','F4'),
                                  command=self.setbindings,
                                  variable=self.ToolType,
                                  value='Relief')
    ToolMenu.menu.add_radiobutton(label='Rocking curve%2s%2s' %('','F5'),
                                  command=self.setbindings,
                                  variable=self.ToolType,
                                  value='Rocker',state=imageplot_state)
    ToolMenu.menu.add_command(label='Close all windows', underline=0,
                              command=self.quit_children)
    ToolMenu['menu']=ToolMenu.menu

    ImageMenu = Menubutton(frameMenubar, text='Image',underline=0)
    ImageMenu.pack(side=LEFT, padx="2m")
    ImageMenu.menu = Menu(ImageMenu)

    ImageMenu.menu.transform =Menu(ImageMenu.menu)
    ImageMenu.menu.add_cascade(label='Transform',menu=ImageMenu.menu.transform)
    ImageMenu.menu.transform.add_checkbutton(label='Flip horizontal',
                                             command=(lambda:self.transform(0,self.FlipHorz.get())),
                                             onvalue=True,
                                             offvalue=False,
                                             variable=self.FlipHorz)
    ImageMenu.menu.transform.add_checkbutton(label='Flip vertical',
                                             command=(lambda:self.transform(1,self.FlipVert.get())),
                                             onvalue=True,
                                             offvalue=False,
                                             variable=self.FlipVert)
    ImageMenu.menu.transform.add_checkbutton(label='Rotate 90',
                                             command=(lambda:self.transform(4,self.Rot90.get())),
                                             onvalue=True,
                                             offvalue=False,
                                             variable=self.Rot90)
    ImageMenu.menu.transform.add_checkbutton(label='Rotate 180',
                                             command=(lambda:self.transform(3,self.Rot180.get())),
                                             onvalue=True,
                                             offvalue=False,
                                             variable=self.Rot180)
    ImageMenu.menu.transform.add_checkbutton(label='Rotate 270',
                                             command=(lambda:self.transform(2,self.Rot270.get())),
                                             onvalue=True,
                                             offvalue=False,
                                             variable=self.Rot270)
    ImageMenu.menu.transform.add_command(label='Reset all',
                                         command=(lambda:self.transform(5)))

###NEW ORIENTATIONS
    ImageMenu.menu.orientation  = Menu(ImageMenu.menu)

    ImageMenu.menu.add_cascade(label='Orientation',
                               menu=ImageMenu.menu.orientation)
    ImageMenu.menu.orientation.add_radiobutton(label='(1,0,0,1)',
                                               command= self.set_orientation ,
                                               value=1,
                                               variable=self.ImOrient)


    ImageMenu.menu.orientation.add_radiobutton(label='(1,0,0,-1)',
                                               command= self.set_orientation ,
                                               value=2,
                                               variable=self.ImOrient)


    ImageMenu.menu.orientation.add_radiobutton(label='(-1,0,0,1)',
                                               command= self.set_orientation ,
                                               value=3,
                                               variable=self.ImOrient)


    ImageMenu.menu.orientation.add_radiobutton(label='(-1,0,0,-1)',
                                               command= self.set_orientation ,
                                               value=4,
                                               variable=self.ImOrient)


    ImageMenu.menu.orientation.add_radiobutton(label='(0,1,1,0)',
                                               command= self.set_orientation ,
                                               value=5,
                                               variable=self.ImOrient)

    ImageMenu.menu.orientation.add_radiobutton(label='(0,1,-1,0)',
                                               command= self.set_orientation ,
                                               value=6,
                                               variable=self.ImOrient)

    ImageMenu.menu.orientation.add_radiobutton(label='(0,-1,1,0)',
                                               command= self.set_orientation ,
                                               value=7,
                                               variable=self.ImOrient)

    ImageMenu.menu.orientation.add_radiobutton(label='(0,-1,-1,0)',
                                               command= self.set_orientation ,
                                               value=8,
                                               variable=self.ImOrient)


#### NEW IMAGE CORRECTION 
    ImageMenu.menu.correction =Menu(ImageMenu.menu)
    ImageMenu.menu.add_cascade(label='Correction..',
                               menu=ImageMenu.menu.correction)
    ImageMenu.menu.correction.add_checkbutton(label='Subtract background',
                                         command=self.bgcorrection,
                                         onvalue=True,
                                         offvalue=False,
                                         variable=self.BgCorrect)
    ImageMenu.menu.correction.add_command(label='Background image',
                                          command=self.OpenBackground)
    ImageMenu.menu.correction.add_checkbutton(label='Flood field correction',
                                         command=self.ffcorrection,
                                         onvalue=True,
                                         offvalue=False,
                                         variable=self.FfCorrect)
    ImageMenu.menu.correction.add_command(label='Flood field image',
                                     command=self.OpenFloodfield)


    ImageMenu['menu']=ImageMenu.menu


###

    CrystMenu = Menubutton(frameMenubar, text='CrystTools',underline=0)
    CrystMenu.pack(side=LEFT, padx="2m")
    CrystMenu.menu =Menu(CrystMenu)
    CrystMenu.menu.peaks =Menu(CrystMenu.menu)
    CrystMenu.menu.add_cascade(label='Peaks..',menu=CrystMenu.menu.peaks)
    CrystMenu.menu.peaks.add_checkbutton(label='Show',
                                         command=self.show_peaks,
                                         onvalue=True,
                                         offvalue=False,
                                         variable=self.ShowPeaks)
    CrystMenu.menu.peaks.add_command(label='Read peaks',
                                     command=self.read_newpeaks)
    CrystMenu.menu.peaks.add_command(label='Options',
                                     command=self.peak_options)
    CrystMenu['menu']=CrystMenu.menu

    self.HistMenu  = Menubutton(frameMenubar, text='History',underline=0)
    self.HistMenu.pack(side=LEFT, padx="2m")
    self.HistMenu.menu =Menu(self.HistMenu)
    self.HistMenu['menu']=self.HistMenu.menu

    HelpMenu = Menubutton(frameMenubar, text='Help',underline=0)
    HelpMenu.pack(side=LEFT, padx="2m")
    HelpMenu.menu =Menu(HelpMenu)
    HelpMenu.menu.add_command(label='Help', underline=0, command=self.help)
    HelpMenu.menu.add_command(label='keybord shortcuts', underline=0,
                              command=self.shortcuts)
    HelpMenu.menu.add_command(label='About', underline=0, command=self.about)
    HelpMenu['menu']=HelpMenu.menu
    frameMenubar.pack(fill=X,side=TOP)
    frameMenubar.tk_menuBar((FileMenu, ToolMenu, CrystMenu, HelpMenu))

  def set_orientation(self,value=None):
    type = self.ImOrient.get()
    if type == 1:
      self.orientation = [1,0,0,1]
    if type == 2:
      self.orientation = [1,0,0,-1]
    if type == 3:
      self.orientation = [-1,0,0,1]
    if type == 4:
      self.orientation = [-1,0,0,-1]
    if type == 5:
      self.orientation = [0,1,1,0]
    if type == 6:
      self.orientation = [0,1,-1,0]
    if type == 7:
      self.orientation = [0,-1,1,0]
    if type == 8:
      self.orientation = [0,-1,-1,0]
    self.gotoimage()
    

  def transform(self,type,value=None):

    if type == 5: # Reset image transformations
      self.FlipHorz.set(False)
      self.FlipVert.set(False)
      self.Rot90.set(False)
      self.Rot180.set(False)
      self.Rot270.set(False)
      self.TransformOrder = []
      self.gotoimage()
      return
    
    if value == True:
      self.TransformOrder.append(type)
    else:
      element = self.TransformOrder.index(type)
      dump = self.TransformOrder.pop(element)
      
    if type == 2:
      (self.xsize, self.ysize)=(self.ysize, self.xsize)
      self.zoomarea=[0,0,self.xsize,self.ysize]
      globals()["image_xsize"] = self.xsize
      globals()["image_ysize"] = self.ysize
      if value == False:
        type = 4
    elif type == 4:
      (self.xsize, self.ysize)=(self.ysize, self.xsize)
      self.zoomarea=[0,0,self.xsize,self.ysize]
      globals()["image_xsize"] = self.xsize
      globals()["image_ysize"] = self.ysize
      if value == False:
        type = 2
    ##### Make sure canvas has the right size
    self.canvas_xsize = int(abs(self.zoomarea[2]-self.zoomarea[0])*\
                              self.zoomfactor)
    self.canvas_ysize = int(abs(self.zoomarea[3]-self.zoomarea[1])*\
                              self.zoomfactor)
    self.canvas.config(width=self.canvas_xsize,height=self.canvas_ysize)
    self.frameScroll.config(width=self.canvas_xsize+30, 
                            height=self.canvas_ysize+30)
    self.noteb1.setnaturalsize() # update size of notebook page

    imean = self.im.meanval # hack to make get_img_stats hack work
    self.im = self.im.transpose(type)
    self.im.meanval = imean  #hack to make get_img_stats hack work
    self.update(self.im)

  def peak_options(self):
    self.peakoptions=Toplevel(self.master)
    self.peakoptions.title('Peak options')
    framepixel = Frame(self.peakoptions, bd=0, bg="white")
    framepixel.pack()
    self.min_pixel.set(globals()["min_pixel"])
    Label(framepixel, 
          text="Show only peaks with more pixels than ").pack(side=LEFT)
    Entry(framepixel, textvariable=self.min_pixel, 
          bg='white', width=6).pack(side=LEFT)
    framepixelcolour = Frame(self.peakoptions, bd=0, bg="white")
    framepixelcolour.pack(fill=X,expand='yes')
    PeakColourSelect = Pmw.ComboBox(framepixelcolour,
                                    label_text="Colour of peak outline ",
                                    labelpos='wn',
                                    dropdown = 2,
                                    listheight=100,
                                    selectioncommand=self.PeakColour,
                                    scrolledlist_items=("red",
                                                        "blue",
                                                        "green",
                                                        "orange",
                                                        "purple"))
    PeakColourSelect.pack()
    PeakColourSelect.selectitem(colour['peak_colour'])

    framepeaksize = Frame(self.peakoptions, bd=0, bg="white")
    framepeaksize.pack(fill=X,expand='yes')
    Label(framepeaksize, text="Radius of peak outline ").pack(side=LEFT)
    Entry(framepeaksize,
          textvariable=self.peak_radius,
          bg='white',
          width=6).pack(side=LEFT,fill=X,expand='yes')

    but = Frame(self.peakoptions, bd=0, bg="white")
    but.pack(side=BOTTOM,fill=X,expand='yes')
    Button(but, text='Update', 
           command=self.update_peak_options).pack(side=LEFT,
                                                  fill=X,
                                                  expand='yes')
    Button(but, text='Close', 
           command=self.setminpixel).pack(side=LEFT,
                                          fill=X,
                                          expand='yes')


  def update_peak_options(self):
    globals()["min_pixel"] = self.min_pixel.get()
    globals()["peak_radius"] = self.peak_radius.get()
    self.update_peaks()
    self.update(newimage=self.im)
    
  def PeakColour(self,entry):
    colour['peak_colour']=entry
    
    
  def setminpixel(self):
    self.update_peaks()
    self.peakoptions.destroy()

  def OpenDialogue(self):
    presentdir = globals()["opendir"]
    fname = askopenfilename(initialdir=presentdir,filetypes=[
      ("EDF files", "*.edf"),
      ("EDF files", "*.cor"),
      ("EDF files compressed", "*.edf.*"),
      ("Tif files", "*.tif"),
      ("Tif files compressed", "*.tif.*"),
      ("MarCCD/Mosaic files", "*.mccd"),
      ("MarCCD/Mosaic files compressed", "*.mccd.*"),
      ("ADSC files", "*.img"),
      ("ADSC files compressed", "*.img.*"),
      ("Bruker files", "*.*"),
      ("Bruker files compressed", "*.*.*"),
      ("All Files", "*")])
    if len(fname) == 0: return
    
    presentdir = os.path.split(fname)[0]
    globals()["opendir"] = presentdir
    return fname
  
  def OpenFile(self,filename=True):
    fname = self.OpenDialogue()
    self.filename.set(fname)
    self.displaynumber.set(fabio.getnum(os.path.split(self.filename.get())[-1]))
    if filename == None: # No image has been opened before
      return 
    else:
      self.gotoimage()

  def OpenBackground(self):
    fname = self.OpenDialogue()
    self.bgimage = openimage.openimage(fname)

  def OpenFloodfield(self):
    fname = self.OpenDialogue()
    self.ffimage = openimage.openimage(fname)

  def bgcorrection(self):
    if self.bgimage == None:
      self.OpenBackground()
    self.gotoimage()
 
  def ffcorrection(self):
    if self.ffimage == None:
      self.OpenFloodfield()
    self.gotoimage()
 
  def rescale(self,event=None):
    self.update()
    return True

  def update(self,newimage=None,filename=None):
    # this function is supposed to intercept any unnecessary calls to update
    # there is no possibility of forcing a scaling through the call - 
    # this will always pick it from the GUI
    s_min=float(self.minval.get())
    s_max=float(self.maxval.get())
    if (self.scaled_min,self.scaled_max,newimage)==(s_min,s_max,None):
      #no need to rescale or redraw
      return

    imageWin.update(self,
                    scaled_min=s_min,
                    scaled_max=s_max,
                    newimage=newimage,
                    orientation=self.orientation,
                    filename=filename)
    self.noteb1.setnaturalsize()
    #store scaling vals for later reference
    self.scaled_min,self.scaled_max=s_min,s_max

  def get_img_stats(self, image):
    #this is a hack _while thinking of a better solution
    #override the imageWin version to use optimized
    #implementation in the specific image classes
    imin,imax=image.getextrema()
    imean= self.im.meanval
    return (imin,imax,imean)
  
  def gotoimage(self,event=None):
    self.master.config(cursor='watch')
    try:
      newfilenumber=int(self.displaynumber.get())
    except:
      newfilenumber = None
      pass
    newfilename = fabio.jump_filename(self.filename.get(),newfilenumber)
    try:
      self.openimage(newfilename)#try to open that file
      self.ErrorInfo.config(text='' , bg='grey85')
    except IOError:
      try:
        #that didn't work - so try the unpadded version
        newfilename=fabio.jump_filename(self.filename.get(),
                                        newfilenumber,
                                        padding=False)
        self.openimage(newfilename)
        self.ErrorInfo.config(text='' , bg='grey85')
      except IOError:
        self.ErrorInfo.config(text='Missing file: %s ' %(newfilename), bg='red')
        self.master.config(cursor='left_ptr')
        #Reset filenumber entry
        self.displaynumber.set(fabio.getnum(self.filename.get()))
        return False
    #image loaded ok

    #set the image dimensions and zoom out if it is big
    screen_width = self.master.winfo_screenwidth()
    screen_height = self.master.winfo_screenheight()
    self.xsize = globals()["image_xsize"]
    self.ysize = globals()["image_ysize"]
    self.zoomfactor = min( round(screen_width/(1.*self.xsize)*10)/10,
                           round(screen_height/(2.*self.ysize)*10)/10)
    self.canvas_xsize = int(abs(self.zoomarea[2]-self.zoomarea[0])*self.zoomfactor)
    self.canvas_ysize = int(abs(self.zoomarea[3]-self.zoomarea[1])*self.zoomfactor)
    self.canvas.config(width=self.canvas_xsize,height=self.canvas_ysize)
    self.frameScroll.config(width=self.canvas_xsize+30,
                            height=self.canvas_ysize+30)
    self.noteb1.setnaturalsize() # update size of notebook page

    ######### SEEMS TO WORK

    self.filename.set(newfilename)
    self.displaynumber.set(newfilenumber)
    self.update(newimage=self.im,
                filename=newfilename)
    self.update_header_page()
    self.update_header_label()
    self.master.config(cursor='left_ptr')
    return True

  def gotohist(self):
    # Open file from  history
    newfilename =self.histfile.get()
    try:
      self.openimage(newfilename)#try to open that file
      try:
        #set the image dimensions and zoom out if it is big
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        self.xsize = globals()["image_xsize"]
        self.ysize = globals()["image_ysize"]
        self.zoomfactor = min( round(screen_width/(1.*self.xsize)*10)/10,
                               round(screen_height/(2.*self.ysize)*10)/10)
        self.canvas_xsize = \
            int(abs(self.zoomarea[2]-self.zoomarea[0])*self.zoomfactor)
        self.canvas_ysize = \
            int(abs(self.zoomarea[3]-self.zoomarea[1])*self.zoomfactor)
        self.canvas.config(width=self.canvas_xsize,
                           height=self.canvas_ysize)
        self.frameScroll.config(width=self.canvas_xsize+30,
                                height=self.canvas_ysize+30)
        self.noteb1.setnaturalsize() # update size of notebook page
      except:
        pass

    except IOError:
      self.ErrorInfo.config(text='Missing file: %s ' %(newfilename), bg='red')
      self.master.config(cursor='left_ptr')
      return False
    #image loaded ok
    self.filename.set(newfilename)
    #HOS self.displaynumber.set(fabio.extract_filenumber(self.filename.get()))
    self.displaynumber.set(fabio.getnum(self.filename.get()))

    self.update(newimage=self.im, filename=newfilename)
    self.update_header_page()
    self.update_header_label()
    self.master.config(cursor='left_ptr')
    return True

  # The time to sleep between update i
  def updatetime(self,event=None):
    if event !=None:
      if event.keysym == 'Up':
        self.sleeptime =self.sleeptime + 0.5
        msg = 'Delay time: %3.1f' %self.sleeptime
        msg_color = 'yellow'
      elif event.keysym == 'Down':
        if self.sleeptime > 0: 
          self.sleeptime=self.sleeptime - 0.5
          msg = 'Delay time: %3.1f' %self.sleeptime
          msg_color = 'yellow'
        else:
          msg = 'Can\'t go any quicker!'
          msg_color = 'red'
      self.ErrorInfo.config(text=msg, bg=msg_color)
         
    
  def autonextimage(self,event=None):
    # If called using keybinding
    if event !=None:
      if event.keysym == 'f':
        if self.autofileupdate.get() == False:
          self.autofileupdate.set(True)
        else:
          self.autofileupdate.set(False)
    # Set Info
    if self.autofileupdate.get():
      msg = 'Delay time: %3.1f' %self.sleeptime
      msg_color = 'yellow'
    else:
      msg = ''
      msg_color = 'grey85'
    self.ErrorInfo.config(text=msg, bg=msg_color)

    #update filename, prefix and number
    self.newfilenumber = int(self.displaynumber.get())+1
    self.newfilename = fabio.jump_filename(self.filename.get(),
                                           self.newfilenumber)
    thread.start_new_thread(self.run,())

  # run thread until autofileupdate is set to False 
  def run(self):
    while(self.autofileupdate.get()==True):
        try:
          self.master.config(cursor='watch')
          self.openimage(self.newfilename)#try to open that file
          self.filename.set(self.newfilename)
          self.displaynumber.set(self.newfilenumber)
          self.update(newimage=self.im,filename=self.newfilename)
          self.update_header_page()
          self.update_header_label()
          self.master.config(cursor='left_ptr')
          self.newfilenumber=int(self.displaynumber.get())+1
          self.newfilename=fabio.jump_filename(self.filename.get(),
                                               self.newfilenumber)
          self.master.config(cursor='left_ptr')
          time.sleep(self.sleeptime)
        except:
          pass
    self.master.config(cursor='left_ptr')

  def nextimage(self,event=None):
    #update filename, prefix and number
    self.master.config(cursor='watch')
    try:
        newfilenumber=int(self.displaynumber.get())+1
    except:
        self.master.config(cursor='left_ptr')
        return True 
    self.displaynumber.set(newfilenumber)
    self.gotoimage()
    return

  def previousimage(self,event=None):
    self.master.config(cursor='watch')
    try:
        newfilenumber=int(self.displaynumber.get())-1
    except:
        self.master.config(cursor='left_ptr')
        return True 
    self.displaynumber.set(newfilenumber)
    self.gotoimage()

  
  def openimage(self,filename=None):
    #if a filename is supplied use that - otherwise get it from the GUI
    # Import fabio 

    if filename==None:
      filename=self.filename.get()

    try:
      img = openimage.openimage(filename)
      if self.BgCorrect.get():
        img.data = img.data.astype(float32)-self.bgimage.data.astype(float32)
      if self.FfCorrect.get():
        img.data = img.data.astype(float32)/self.ffimage.data.astype(float32)

      # The -1 in front of o11,o12 etc is accomodate for
      # Rot180 made on the screen
      img.data = image_flipping(img.data,
                                -1*self.orientation[0],
                                -1*self.orientation[1],
                                -1*self.orientation[2],
                                -1*self.orientation[3])
      (img.dim2, img.dim1) = img.data.shape
      self.im = img.toPIL16()
      # We have earlier on used a flip making a PIL image
      # to keep images in the same direction we do the same here
      #self.im = self.im.transpose(1)
      
      (self.xsize, self.ysize)=(img.dim1, img.dim2)
    except IOError:
      raise

    # Check image oriention
    for type in self.TransformOrder:
	self.im=self.im.transpose(type)
        if type == 4 or type == 2:
          (self.xsize, self.ysize)=(self.ysize, self.xsize)

#     if self.FlipHorz.get() == True:
# 	self.im=self.im.transpose(0)
#     if self.FlipVert.get() == True:
# 	self.im=self.im.transpose(1)
#     if self.Rot90.get() == True:
# 	self.im=self.im.transpose(4)
# 	(self.xsize, self.ysize)=(self.ysize, self.xsize)
#     if self.Rot180.get() == True:
# 	self.im=self.im.transpose(3)
#     if self.Rot270.get() == True:
# 	self.im=self.im.transpose(2)
# 	(self.xsize, self.ysize)=(self.ysize, self.xsize)
        
    (self.im.minval,self.im.maxval,self.im.meanval)=(img.getmin(),
                                                     img.getmax(),
                                                     img.getmean())
    self.im.header=img.getheader()
    self.zoomarea=[0,0,self.xsize,self.ysize]
    self.master.title("fabian - %s" %(filename))
    globals()["image_xsize"] = self.xsize
    globals()["image_ysize"] = self.ysize

    # Make/update file history
    maxlen = 20

    if filename not in self.HistMenuItems:
      if self.histlength > maxlen:
        self.HistMenu.menu.delete(1)
        self.HistMenuItems[:maxlen] = self.HistMenuItems[1:maxlen+1]
        self.HistMenuItems[maxlen] = filename
      else:
        self.histlength = self.histlength + 1
        self.HistMenuItems.append(filename)

      self.HistMenu.menu.add_radiobutton(label=filename,
                                         command=self.gotohist,
                                         variable=self.histfile,
                                         value=filename)
      self.histfile.set(filename)
    
      
  def about(self,event=None):
    About.About()
  def shortcuts(self,event=None):
    Shortcuts.show()

  def help(self,event=None):
    import webbrowser
    webbrowser.open('http://sourceforge.net/apps/trac/fable/wiki/fabian')


