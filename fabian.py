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
import Numeric
import math
import edfimage, tifimage, adscimage, brukerimage, marccdimage,bruker100image,pnmimage
from string import *
from PIL import Image, ImageTk, ImageFile, ImageStat
from tkFileDialog import *
import tkFont
import re,os,sys,time
from sets import Set as set

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

colour={'transientaoi':'RoyalBlue', 'Zoom':'red', 'Relief':'LimeGreen', 'Rocker':'LightBlue', 'transientline':'red', 'LineProfile':'RoyalBlue'}

      
class imageWin:
  def __init__(self,master,filename=None,filenumber=0,title=None,zoomfactor=1,scaled_min=None,scaled_max=None,scale=None, mainwin='no',zoomable='yes',coords=[0,0,0,0],image=None,tool=None):
    #initialize var
    self.master=master
    #these keep track of the AOIs
    self.aoi=[]
    self.zoom_win = 0
    self.line_win = 0
    self.offset=0
    self.transientaoi=None
    self.transientline=None
    self.maxval=StringVar()
    self.minval=StringVar()
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
      self.draw2=self.drawLine2
    else:
      self.draw2=self.drawAoi2
    master.bind('<F1>',self.updatebindings)
    master.bind('<F2>',self.updatebindings)
    master.bind('<F3>',self.updatebindings)
    master.bind('<F4>',self.updatebindings)
    master.bind('q',self.quit)
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
    
    frame = Frame(master, bd=0, bg="white") #, width=600, height=600) 
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
    frameImage = Frame(container, bd=0, bg="white")
    self.canvas = Canvas(frameImage, width=self.canvas_xsize, height=self.canvas_ysize)
    self.canvas.pack(side=TOP,fill=BOTH, expand='yes')
    frameImage.pack(side=TOP,expand=1, pady=10, padx=5)
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
  
  def rezoom(self,e):
    if e.keysym=='z':
      #print "i am rezoom()",e.keysym
      newzoomfactor=self.zoomfactor*2
    elif e.keysym=='x':
      #print "i am rezoom()",e.keysym
      newzoomfactor=self.zoomfactor/2.
    self.canvas_xsize = int(abs(self.zoomarea[2]-self.zoomarea[0])*newzoomfactor)
    self.canvas_ysize = int(abs(self.zoomarea[3]-self.zoomarea[1])*newzoomfactor)
    self.canvas.config(width=self.canvas_xsize, height=self.canvas_ysize)
    #just figured out that one could do this
    self.canvas.scale('all',0,0,newzoomfactor/self.zoomfactor,newzoomfactor/self.zoomfactor)
    self.zoomfactor=newzoomfactor
    self.ShowZoom.config(text="%3d %%" %(newzoomfactor*100))
    self.update(newimage=self.im)
 
  def make_status_bar(self,container):
    frameInfo = Frame(container, bd=0, bg="white")
    self.ShowMin = Label(frameInfo, text="Min -1",  bg ='white',bd=1, relief=SUNKEN, anchor=W)
    self.ShowMin.pack(side=LEFT)
    self.ShowMax = Label(frameInfo, text="Max -1" , bg ='white',bd=1, relief=SUNKEN, anchor=W)
    self.ShowMax.pack(side=LEFT)
    self.ShowMean = Label(frameInfo, text="Mean -1", bg ='white',bd=1, relief=SUNKEN, anchor=W)
    self.ShowMean.pack(side=LEFT)
    self.ShowInt = Label(frameInfo, text='    0', width=5, bg='white', bd=1, relief=RIDGE, anchor=W)
    self.ShowInt.pack(side=RIGHT, padx=2)
    self.ShowCoor = Label(frameInfo, text='    0,    0', width =10, bg ='white',bd=1, relief=RIDGE, anchor=W)
    self.ShowCoor.pack(side=RIGHT, padx = 2)
    self.ShowZoom = Label(frameInfo, text="%3d %%" %(self.zoomfactor*100), width =6, bg ='white',bd=1, relief=RIDGE, anchor=W)
    self.ShowZoom.pack(side=RIGHT, padx = 2)
    frameInfo.pack(side=LEFT, pady=10, padx=5)
    frameInfo.pack(side=TOP,fill=X)

  def MouseMotion(self,event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasx(event.y)
    if x<self.canvas_xsize and y<self.canvas_ysize:
      xy =  "%5i,%5i"%(x/self.zoomfactor +self.zoomarea[0],y/self.zoomfactor +self.zoomarea[1])
      self.ShowCoor.config(text=xy)
      I = "%5.0f"% self.im.getpixel((x/self.zoomfactor +self.zoomarea[0],y/self.zoomfactor +self.zoomarea[1]))
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
    self.drawAoi2()
  def Mouse3Release(self, event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasy(event.y)
    x,y=self.val_canvas_coord((x,y))
    self.transientcorners[2:]=[x,y]
    #save whichever tool was active
    tmp=self.draw2
    self.draw2=self.drawAoi2
    self.use_tool(tool='Zoom')
    self.draw2=tmp
    
  def Mouse1Press(self, event):
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
    if 'Relief' in tool:
        if self.transientcorners[0]==self.transientcorners[2] or self.transientcorners[1]==self.transientcorners[3]:
          self.canvas.delete('transientaoi')
          return
	if 'zoom' in self.master.wm_title():
          t= 'relief of ' + self.master.wm_title()
        else:
          t='relief of main'
	opensubwin=self.openrelief
    elif 'Zoom' in tool:
        if self.transientcorners[0]==self.transientcorners[2] or self.transientcorners[1]==self.transientcorners[3]:
          self.canvas.delete('transientaoi')
          return
        if 'zoom' in self.master.wm_title():
          t= self.master.wm_title() +'.%d' %  self.zoom_win
        else:
          t='zoom %d' % self.zoom_win
        opensubwin=self.openzoom
        self.zoom_win=self.zoom_win+1
    elif 'Rock' in tool:
	t = 'rock'
	opensubwin=self.openrocker
    elif 'Line' in tool:
      if self.transientcorners[:2]==self.transientcorners[2:]:
        self.canvas.delete('transientline')
        return
      if 'zoom' in self.master.wm_title():
        t= self.master.wm_title() +'.%d' %  self.line_win
        self.line_win = self.line_win + 1
      else:
        t='Line %d of main' % self.line_win
        self.line_win = self.line_win + 1
      opensubwin=self.openlineprofile
    self.aoi.append({'coords':self.transientcorners,'aoi':[self.draw2(tool=tool)],'zoomwin': opensubwin(t), 'wintype':tool})

  def drawAoi2(self,tool='transientaoi'):
    self.canvas.delete('transientaoi')
    return self.canvas.create_rectangle(self.transientcorners,tag=tool,outline=colour[tool])

  def drawLine2(self,tool='transientline'):
    self.canvas.delete('transientline')
    t_end=4
    tc=self.transientcorners
    #calc the end section coordinates
    endsec = Numeric.array([tc[2]-tc[0], tc[3]-tc[1]])
    normendsec = math.sqrt(sum(endsec*endsec))
    if normendsec == 0:
      #line has no length - i.e. no line should be drawn and no plot should be opened (no?)
      return
    else:
      endsec = endsec/normendsec*t_end
      #line is drawn as a polyline in one single object
      line=(tc[0]-endsec[1],tc[1]+endsec[0],tc[0]+endsec[1],tc[1]-endsec[0],tc[0],tc[1],tc[2],tc[3],tc[2]-endsec[1],tc[3]+endsec[0],tc[2]+endsec[1],tc[3]-endsec[0])
    return self.canvas.create_line(line,tag=tool,fill=colour[tool])

 
  def openzoom(self,tag):
    t=self.transientcorners
    corners=[int(self.zoomarea[0]+t[0]/self.zoomfactor), int(self.zoomarea[1]+t[1]/self.zoomfactor), int(self.zoomarea[0]+t[2]/self.zoomfactor), int(self.zoomarea[1]+t[3]/self.zoomfactor)]
    if corners[0]-corners[2] == 0 or corners[1]-corners[3] == 0: return False
    w=Toplevel(self.master)
    if self.tool:
      newwin=imageWin(w,title=tag,filename=self.filename,zoomfactor=self.zoomfactor*4,scaled_min=self.minval.get(),scaled_max=self.maxval.get(),scale=self.scale,coords=corners,image=self.im,tool=self.tool)
      newwin.tool=self.tool
    else:
      newwin=imageWin(w,title=tag,filename=self.filename,zoomfactor=self.zoomfactor*4,coords=corners,image=self.im,tool=None)
    return newwin

  def openlineprofile(self,tag):
      # Make lineprofile  relief window
      import pixel_trace
      w=Toplevel(self.master)
      t=self.transientcorners
      corners=[(self.zoomarea[0]+t[0]/self.zoomfactor), (self.zoomarea[1]+t[1]/self.zoomfactor), (self.zoomarea[0]+t[2]/self.zoomfactor-1), (self.zoomarea[1]+t[3]/self.zoomfactor)-1]
      pixels = pixel_trace.pixel_trace(corners)
      t = []
      pixval = []
      path = 0
      for i in range(len(pixels)):
        path = path + pixels[i][2]
        t.append(i)
        pixval.append(self.im.getpixel((pixels[i][0],pixels[i][1])))
      linewin = imagePlot(w,title=tag,x=t,y=pixval)
      return linewin
    
  def openrelief(self,tag):
      # Make 3D relief window
      t=self.transientcorners
      corners=[int(self.zoomarea[0]+t[0]/self.zoomfactor), int(self.zoomarea[1]+t[1]/self.zoomfactor), int(self.zoomarea[0]+t[2]/self.zoomfactor), int(self.zoomarea[1]+t[3]/self.zoomfactor)]
      
      reli=Toplevel(self.master)
      reli.title(tag)
      newReli=ReliefPlot(reli,newimage=self.im,corners=corners)
      return newReli

  def openrocker(self,tag):
      # Make 3D relief window
      t=self.transientcorners
      self.corners=[int(self.zoomarea[0]+t[0]/self.zoomfactor), int(self.zoomarea[1]+t[1]/self.zoomfactor), int(self.zoomarea[0]+t[2]/self.zoomfactor), int(self.zoomarea[1]+t[3]/self.zoomfactor)]
      self.center = deconstruct_filename(self.filename.get())[0]
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
      Radiobutton(radio1,text='Rocking curve +/- ', variable=self.seriestype, value='delta',anchor=W).pack(side=LEFT,fill=BOTH)
      e=Entry(radio1, textvariable=self.delta, bg='white', width=6)
      e.bind('<FocusIn>',self.setradio1)
      e.pack(side=LEFT)
      Label(radio1, text="frames").pack(side=LEFT)
      radio1.pack(fill=BOTH)
      radio2 = Frame(frame)
      Radiobutton(frame,text='Rocking curve from frame', variable=self.seriestype, value='startend',anchor=W).pack(side=LEFT,fill=BOTH)
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
    import rocker
    rockdata = rocker.rocker(filename_sample=self.filename.get(), coord=self.corners, startnumber=startframe, endnumber=endframe)
    rockdata.run()
    w=Toplevel(self.master)
    linewin = imagePlot(w,title='Rocking curve',x=rockdata.imagenumber,y=rockdata.getdata())
    return linewin
  
  def setradio1(self,event=None): # Sets the radiobuttom to make fileseries from -x to +x images from current
      self.seriestype.set('delta')

  def setradio2(self,event=None):  # Sets the radiobuttom to make fileseries from No.X to No Y.
      self.seriestype.set('startend')

  def get_img_stats(self, image):
    #this is a hack _while thinking of a better solution
    imin,imax=image.getextrema()
    l=list(image.getdata())
    imean=sum(l)/len(l)
    return (imin,imax,imean)
   
  def update(self,scaled_min=0,scaled_max=0,newimage=None,filename=None):
    if self.scale==0:
      self.reset_scale()
    if (scaled_min==scaled_max==0):
      scaled_min = atof(self.minval.get())
      scaled_max = atof(self.maxval.get())
    else:
      self.minval.set(scaled_min)
      self.maxval.set(scaled_max)
    self.scale = 255.0 / (scaled_max - scaled_min)
    self.offset = - scaled_min * self.scale
    
    if newimage: self.im=newimage
    imcrop = self.im.crop(self.zoomarea)
    im8c = imcrop.point(lambda i: i * self.scale + self.offset).convert('L')
    self.img = ImageTk.PhotoImage(im8c.resize((self.canvas_xsize,self.canvas_ysize)))
    self.im_min,self.im_max,self.im_mean = self.get_img_stats(imcrop)

    self.ShowMin.config(text="Min %i" %(self.im_min))
    self.ShowMax.config(text="Max %i" %(self.im_max))
    self.ShowMean.config(text="Mean %i" %(self.im_mean))
    self.canvas.lower(self.canvas.create_image(0,0,anchor=NW, image=self.img))

    #update children
    for w in self.aoi:
      if w['wintype'] in ('Zoom'):
        w['zoomwin'].update(scaled_min,scaled_max,newimage=newimage)
      if w['wintype'] in ('LineProfile'):
        w['zoomwin'].update(coord=w['coords'],zoomarea=self.zoomarea,zoomfactor=self.zoomfactor,newimage=newimage)
      if w['wintype'] in ('Relief'):
        w['zoomwin'].update(newimage=self.im)
    return True
  
  def reset_scale(self):
    #find best image grayscale for the present image.
    #only to be called when this is the main window instance
    self.im_min,self.im_max = self.im.getextrema()
    self.maxval.set(self.im_max)
    self.minval.set("%.0f"%self.im_min)
    hist = self.im.histogram()
    i = 2
    cc = sum(hist[:i+1])
    while cc < 0.98*sum(hist) and i < 255:
      i=i+1
      cc = cc + hist[i]
    scaled_max = max(1,((self.im_max - self.im_min)/255 *i)+self.im_min)
    self.maxval.set("%.0f"%scaled_max)

  def setbindings(self):
    try:
      self.tool = self.ToolType.get()
    except:
      pass
    if 'LineProfile' in self.tool:
      self.draw2=self.drawLine2
    else:
      self.draw2=self.drawAoi2
    #update children
    for w in self.aoi:
      if w['wintype']=='Zoom':
	w['zoomwin'].tool=self.tool
	w['zoomwin'].setbindings()

  def updatebindings(self,tool=None):
    print event.keysym
    if event.keysym=='F1':
      try:
        self.ToolType.set('Zoom')
      except:
        self.tool = 'Zoom'
      self.setbindings()
    if event.keysym=='F2':
      try:
        self.ToolType.set('LineProfile')
      except:
        self.tool='LineProfile'
      self.setbindings()
    if event.keysym=='F3':
      try:
        self.ToolType.set('Relief')
      except:
        self.tool='Relief'
      self.setbindings()
    if event.keysym=='F4':
      try:
        self.ToolType.set('Rocker')
      except:
        self.tool='Rocker'
      self.setbindings()

  def quit(self,event=None):
    self.master.destroy()

class appWin(imageWin):
  def __init__(self,master,filenumber=0,filename=None,filetype=None,zoomfactor=1,mainwin='no',zoomable='yes',coords=[0,0,0,0],image=None):
    #initialize var
    self.master=master
    #these keep track of the AOIs
    self.aoi=[]
    self.zoom_win = 0
    self.line_win = 0
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
    self.filetype = filetype
    self.ToolType = StringVar()
    self.tool = 'Zoom' # Set default event of mouse bottom 1 to Zoom  
    self.draw2=self.drawAoi2
    self.ToolType.set(self.tool)
    master.bind('<F1>',self.updatebindings)
    master.bind('<F2>',self.updatebindings)
    master.bind('<F3>',self.updatebindings)
    master.bind('<F4>',self.updatebindings)
    master.bind('o',self.OpenFile)
    master.bind('q',self.quit)
    master.bind('a',self.about)
    master.bind('<FocusIn>',self.MouseEntry)
    master.bind('z',self.rezoom)
    master.bind('x',self.rezoom)
    
    if filename:
      self.filename.set(filename)
      (newfilenumber,filetype)=deconstruct_filename(filename)
      self.displaynumber.set(newfilenumber)
      if not filetype:
        self.filetype=os.path.splitext(filename)[1][1:]
      else:
        self.filetype=filetype
    else:
      self.OpenFile(filename=None)

    self.zoomfactor=zoomfactor
    #display image and reset scale if scaling is not given
    self.openimage()
    self.reset_scale()

    self.zoomarea = [0,0,self.xsize,self.ysize]
    #set the image dimensions and zoom out if it is big
    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    self.zoomfactor = min( round(screen_width/(1.*self.xsize)*10)/10, round(screen_height/(2.*self.ysize)*10)/10)
#    self.zoomfac
    frame = Frame(master, bd=0, bg="white")
    frame.pack(fill=X)

    #add menubar
    self.make_command_menu(frame)

    #Add Notebook tabs
    self.noteb1 = Pmw.NoteBook(frame)
    self.noteb1.pack(side=BOTTOM,fill='both')
    self.page1 = self.noteb1.add('Image')
    self.page2 = self.noteb1.add('Info')
    

    #call __init__ in the parent class
    self.make_scaling_ctls(self.page1)
    self.can = Frame(self.page1, bd=0, bg="white")
    self.can.pack(fill=X)

    self.scrollscanvas = Pmw.ScrolledCanvas(self.can, labelpos=N, usehullsize =1, hull_width=600, hull_height=600)
    self.scrollscanvas.pack(fill=BOTH, expand=YES)
    self.scroll = self.scrollscanvas.interior()

    self.make_image_canvas(self.scroll)
    
    self.make_header_info()
    self.make_status_bar(self.page1)
    self.noteb1.setnaturalsize()
    
    # Put header on page2 Info
    self.HeaderFrame = Pmw.ScrolledFrame(self.page2, labelpos=N)
    self.HeaderFrame.pack(fill=BOTH, expand=YES)
    self.HeaderInterior = self.HeaderFrame.interior()
    self.make_header_page()
    
    #run update to set scalings and actually display the images
    #change this to draw/redraw set of functions at some point?
    self.update()
    self.setbindings()

    

  def make_header_page(self):
      self.headcheck=[]
      self.headtext={}
      self.newitem={}
      for item in self.im.header:
        fm = Frame(self.HeaderInterior)
        self.newitem[item]=StringVar()
        c=Checkbutton(fm,text='%s' %(item), command=self.update_header_label,variable=self.newitem[item], bg='white',anchor=W,width=20).pack(side=LEFT,anchor=W)
        self.headcheck.append(c)
        #self.headcheck.append(Checkbutton(fm,tag='headercheck',text='%s' %(item), command=self.update_header_label,variable=self.newitem[item], bg='white',anchor=W,width=20).pack(side=LEFT,anchor=W))
        self.headtext[item]= Label(fm,text='%s' %(self.im.header[item]), bg='white',anchor=W,width=100)
        self.headtext[item].pack(side=LEFT,fill=X,expand='yes')
        fm.pack(side=TOP,anchor=W)

  def make_header_info(self):
    self.HeaderInfo = Label(self.page1, text='', anchor=W)
    self.HeaderInfo.pack(side=TOP,fill=BOTH)
    
  def clear_header_page(self):
    for child in self.HeaderInterior.winfo_children():
      child.destroy()

  def update_header_page(self):
    #check if the set of (possibly newly read from disk) header items is compatible with the ones displayed
    if set(self.im.header.keys())==set(self.headtext.keys()):
      #they seem to be compatible, note - this keeps the checked checkboxes alive
      for item,value in self.im.header.iteritems():
        self.headtext[item].config(text='%s' % value)
    else:
      #they differ - make a new header page from scratch
      self.clear_header_page()
      self.make_header_page()
      
  def update_header_label(self):
    headertext = ''
    for item in self.newitem:
      if self.newitem[item].get() == '1':
            headertext = headertext+item+': '+self.im.header[item] +'; '
    self.HeaderInfo.config(text='%s' %(headertext))

        
  def make_scaling_ctls(self,master):
    frameScale = Frame(master, bd=0, bg="white")
    # Image scale controls  
    Label(frameScale,text='Scale: ', bg='white').pack(side=LEFT)
    Label(frameScale,text='min:', bg='white').pack(side=LEFT)
    e=Entry(frameScale, textvariable=self.minval, bg='white', width=6)
    #e.bind('<FocusOut>',self.rescale)
    e.bind('<Return>',self.rescale)
    e.bind('<KP_Enter>',self.rescale)
    e.pack(side=LEFT,padx=4)
    Label(frameScale,text='max:', bg='white').pack(side=LEFT)
    e=Entry(frameScale, textvariable=self.maxval, bg='white', width=6)
    #e.bind('<FocusOut>',self.rescale)
    e.bind('<Return>',self.rescale)
    e.bind('<KP_Enter>',self.rescale)
    e.pack(side=LEFT,padx=4)
    
    Button(frameScale,text='update', bg='white', command=self.update).pack(side=LEFT,padx=2)
    Button(frameScale,text='reset', bg='white', command=self.reset_scale).pack(side=LEFT,padx=2)
    
    Button(frameScale,text='next', bg='white', command=self.nextimage).pack(side=RIGHT)
    Button(frameScale,text='previous', bg='white', command=self.previousimage).pack(side=RIGHT)
    e=Entry(frameScale, textvariable=self.displaynumber, bg='white', width=6)
    e.bind('<FocusOut>',self.gotoimage)
    e.bind('<Return>',self.gotoimage)
    e.bind('<KP_Enter>',self.gotoimage)
    e.pack(side=RIGHT,padx=8)
    Button(frameScale,text='go to number:', bg='white', command=self.gotoimage).pack(side=RIGHT,padx=2)
    frameScale.pack(side=TOP,expand=1, pady=10, fill=X)
     
  def make_command_menu(self,master):
    frameMenubar = Frame(master,relief=RAISED, borderwidth=2)
    FileMenu = Menubutton(frameMenubar, text='File',underline=0)
    FileMenu.pack(side=LEFT, padx="2m")
    FileMenu.menu =Menu(FileMenu)
    FileMenu.menu.add_command(label='Open', underline=0, command=self.OpenFile)
    FileMenu.menu.add_command(label='Quit', underline=0, command=self.quit)
    FileMenu['menu']=FileMenu.menu

    ToolMenu = Menubutton(frameMenubar, text='Tools',underline=0)
    ToolMenu.pack(side=LEFT, padx="2m")
    ToolMenu.menu =Menu(ToolMenu)
    ToolMenu.menu.add_radiobutton(label='Zoom%15s%2s' %('','F1') ,command=self.setbindings,variable=self.ToolType,value='Zoom')
    ToolMenu.menu.add_radiobutton(label='Line profile%7s%2s' %('','F2') ,command=self.setbindings,variable=self.ToolType,value='LineProfile')
    ToolMenu.menu.add_radiobutton(label='Relief plot%8s%2s' %('','F3') ,command=self.setbindings,variable=self.ToolType,value='Relief')
    ToolMenu.menu.add_radiobutton(label='Rocking curve%2s%2s' %('','F4'),command=self.setbindings,variable=self.ToolType,value='Rocker')
    ToolMenu['menu']=ToolMenu.menu

    HelpMenu = Menubutton(frameMenubar, text='Help',underline=0)
    HelpMenu.pack(side=LEFT, padx="2m")
    HelpMenu.menu =Menu(HelpMenu)
    HelpMenu.menu.add_command(label='About', underline=0, command=self.about)
    HelpMenu['menu']=HelpMenu.menu
    frameMenubar.pack(fill=X,side=TOP)
    frameMenubar.tk_menuBar((FileMenu, ToolMenu, HelpMenu))

  def OpenFile(self,filename=True):
    fname = askopenfilename(filetypes=[("EDF files", "*.edf"),("Tif files", "*.tif"),("MarCCD/Mosaic files", "*.mccd"),("ADSC files", "*.img"),("Bruker files", "*.*"),("All Files", "*")])
    if len(fname) == 0: return
    self.filename.set(fname)
    (newfilenumber,filetype)=deconstruct_filename(self.filename.get())
    self.filetype=filetype
    self.displaynumber.set(newfilenumber)
    if filename == None: # No image has been opened before
      return 
    else:
      self.gotoimage()
      try:
        #set the image dimensions and zoom out if it is big
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        self.zoomfactor = min( round(screen_width/(1.*self.xsize)*10)/10, round(screen_height/(2.*self.ysize)*10)/10)
        self.canvas_xsize = int(abs(self.zoomarea[2]-self.zoomarea[0])*self.zoomfactor)
        self.canvas_ysize = int(abs(self.zoomarea[3]-self.zoomarea[1])*self.zoomfactor)
        self.canvas.config(width=self.canvas_xsize,height=self.canvas_ysize)
        self.noteb1.setnaturalsize() # update size of notebook page
      except:
        pass
 
  def rescale(self,event=None):
    self.update()
    return True

  def update(self,newimage=None,filename=None):
    #this function is supposed to intercept any unnecessary calls to update
    #there is no possibility of forcing a scaling through the call - this will always pick it from the GUI
    s_min=atof(self.minval.get())
    s_max=atof(self.maxval.get())
    if (self.scaled_min,self.scaled_max,newimage)==(s_min,s_max,None):
      #no need to rescale or redraw
      return
    imageWin.update(self,scaled_min=s_min,scaled_max=s_max,newimage=newimage,filename=filename)
    self.noteb1.setnaturalsize()
    #store scaling vals for later reference
    self.scaled_min,self.scaled_max=s_min,s_max

  def get_img_stats(self, image):
    #this is a hack _while thinking of a better solution
    #override the imageWin version to use optimized
    #implementation in the specific image classes
    imin,imax=image.getextrema()
    imean=self.im.meanval
    return (imin,imax,imean)
  
  def gotoimage(self,event=None):
    newfilenumber=int(self.displaynumber.get())
    newfilename=construct_filename(self.filename.get(),newfilenumber)
    try:
      self.openimage(newfilename)#try to open that file
    except IOError:
      try:
        #that didn't work - so try the unpadded version
        newfilename=construct_filename(self.filename.get(),newfilenumber,padding=False)
        self.openimage(newfilename)
      except IOError:
        e=Error()
        msg="No such file: %s " %(newfilename)
        e.Er(msg)
        return False
    #image loaded ok
    self.update(newimage=self.im,filename=newfilename)
    self.update_header_page()
    self.update_header_label()
    self.filename.set(newfilename)
    self.displaynumber.set(newfilenumber)
    return True

  def nextimage(self):
    #update filename, prefix and number
    newfilenumber=int(self.displaynumber.get())+1
    newfilename=construct_filename(self.filename.get(),newfilenumber)
    try:
      self.openimage(newfilename)#try to open that file
    except IOError:
      e=Error()
      msg="No such file: %s " %(newfilename)
      e.Er(msg)
      return False
    #image loaded ok
    self.update(newimage=self.im,filename=newfilename)
    self.update_header_page()
    self.update_header_label()
    self.filename.set(newfilename)
    self.displaynumber.set(newfilenumber)
    return True
      
  def previousimage(self):
    newfilenumber=int(self.displaynumber.get())-1
    try:
      newfilename=construct_filename(self.filename.get(),newfilenumber)
      self.openimage(newfilename)#try to open that file
    except IOError:
      try:
        #that didn't work - so try the unpadded version
        newfilename=construct_filename(self.filename.get(),newfilenumber,padding=False)
        self.openimage(newfilename)
      except IOError:
        e=Error()
        msg="No such file: %s " %(newfilename)
        e.Er(msg)
        return False
    #image loaded ok
    self.update(newimage=self.im,filename=newfilename)
    self.update_header_page()
    self.update_header_label()
    self.filename.set(newfilename)
    self.displaynumber.set(newfilenumber)
    return True
  
  def openimage(self,filename=None):
    #if a filename is supplied use that - otherwise get it from the GUI
    if filename==None:
      filename=self.filename.get()
    #if the filetype instance variable is set use that - otherwise extract it from the filename extension
    if self.filetype:
      filetype=self.filetype
    else:
      filetype=os.path.splitext(filename)[1][1:]
    
    img=eval( filetype+'image.'+filetype+'image()')
    try:
      self.im=img.read(filename).toPIL16()
      (self.im.minval,self.im.maxval,self.im.meanval)=(img.getmin(),img.getmax(),img.getmean())
      self.im.header=img.getheader()
      (self.xsize, self.ysize)=(img.dim1, img.dim2)
    except IOError:
      raise
    self.zoomarea=[0,0,self.xsize,self.ysize]
    self.master.title("fabian - %s" %(filename))

      
  def about(self,event=None):
    About()
    
#  def quit(self):
#    self.master.destroy()

class imagePlot:
  def __init__(self,master,title='Plot',x=None,y=None):
      self.master = master
      self.master.title(title)
      self.frame = Frame(self.master)
      self.frame.pack()
      self.f = Figure(figsize=(8,5), dpi=100)
      self.a = self.f.add_subplot(111)
      self.plotcanvas = FigureCanvasTkAgg(self.f, master=self.master)
      self.plotcanvas.show()
      self.plotcanvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
      #self.f.xticks(x)
      self.a.plot(x, y, 'b-')

  def setbindings(self):
    pass

  def update(self,coord=[0,0,0,0],zoomarea=[0,0,0,0],zoomfactor=1, newimage=None):
      import pixel_trace
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


class ReliefPlot:
    def __init__(self,master,newimage=None,corners=[0,0,0,0]):
        import OpenGL.GL as GL
        import OpenGL.Tk as oTk
        self.master = master
        self.f=oTk.Frame(self.master)
        self.f.pack(side=oTk.BOTTOM,expand=oTk.NO,fill=oTk.X)
        self.dataoff=0
        self.corners = corners
        data = list(newimage.crop(self.corners).getdata())
        extrema = [min(data),max(data)]
        data = Numeric.reshape( data,[self.corners[3]-self.corners[1], self.corners[2]-self.corners[0]])
        self.map=data.copy()
        self.pointsize=4.

        self.map = Numeric.transpose(self.map)
        self.sizex = self.map.shape[0]
        self.sizey = self.map.shape[1]
        self.size = (self.sizex+ self.sizey)/2.0
        self.zscale = self.size/(extrema[1]-extrema[0])
        self.map = self.map*self.zscale
        if self.sizex > self.sizey:
          self.scale = 0.75/self.sizex
        else:
          self.scale = 0.75/self.sizey
        self.zcenter = -(extrema[1]+extrema[0])*self.zscale/2.0
        self.reliefWin = oTk.Opengl(self.f,width = 500, height = 500, double = 1)
        self.reliefWin.redraw = self.redraw
        self.reliefWin.autospin_allowed = 1
        self.reliefWin.fovy=5
        self.reliefWin.near=1e2
        self.reliefWin.far=1e-6
        import math
        self.reliefWin.pack(side = oTk.TOP, expand = oTk.YES, fill = oTk.BOTH)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        oTk.Button(self.f,text="Help",command=self.reliefWin.help).pack(side=oTk.LEFT)
        oTk.Button(self.f,text="Reset",command=self.reliefWin.reset).pack(side=oTk.LEFT)
        oTk.Button(self.f,text="Quit",command=self.quit).pack(side=oTk.RIGHT)

    def setbindings(self):
      pass
    
    def quit(self):
        self.master.destroy()
    
    def update(self,newimage=None):
        data = list(newimage.crop(self.corners).getdata())
        extrema = [min(data),max(data)]
        data = Numeric.reshape( data,[self.corners[3]-self.corners[1], self.corners[2]-self.corners[0]])
        self.map = data.copy()
        self.map = Numeric.transpose(self.map)
        self.zscale = self.size/(extrema[1]-extrema[0])
        self.map = self.map*self.zscale
        if self.sizex > self.sizey:
          self.scale = 0.75/self.sizex
        else:
          self.scale = 0.75/self.sizey
        self.zcenter = -(extrema[1]+extrema[0])*self.zscale/2.0
        self.reliefWin.tkRedraw() # Redraw canvas
        
    def redraw(self,reliefWin):
         import OpenGL.GL as GL
         GL.glClearColor(0., 0., 0., 0)
         GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
         GL.glOrtho(-1,1,-1,1,-1,1)
         GL.glDisable(GL.GL_LIGHTING)
         GL.glColor3f(1.0, 1.0, 1.0) # white
         GL.glPointSize(self.pointsize)
         GL.glPushMatrix()
         GL.glScale(self.scale,self.scale,self.scale)
         GL.glRotate(-20,0,0,1)
         GL.glRotate(-110,1,0,0)
         GL.glTranslatef(-self.sizex/2.0,-self.sizey/2.0,self.zcenter)
         for i in range(self.sizex):
             GL.glBegin(GL.GL_LINE_STRIP)
             for j in range(self.sizey):
                 GL.glVertex3f(i,j,self.map[i][j])
             GL.glEnd()
         for i in range(self.sizey):
             GL.glBegin(GL.GL_LINE_STRIP)
             for j in range(self.sizex):
                 GL.glVertex3f(j,i,self.map[j][i])
             GL.glEnd()
         GL.glEnable(GL.GL_LIGHTING)
         GL.glPopMatrix()

class Error:
    def Er(self,message):
        self.master = Tk()
        self.master.title('Error!')
        frame = Frame(self.master, width=500, height=400, bd=1)
        frame.pack()

        frameTitle = Frame(frame)
        Label(frameTitle,text='Bummer - YOU made an error').pack(side=LEFT)
        frameTitle.pack(expand=1, pady=10, padx=5)

        frameError = Frame(frame, bd=0)
        Message(frameError, text=message,width=500).pack(fill=X, padx=5)
        frameError.pack(expand=1, pady=10, padx=5)

        frameError = Frame(frame, bd=0)
        Button(frameError,text='Too bad', bg='red', command=self.quit)\
                                          .pack(side=RIGHT)
        frameError.pack(expand=1, pady=10, padx=5)
        
    def quit(self):
        self.master.destroy()

class About:
    def __init__(self):
        self.master = Tk()
        self.master.title('About fabian')
        frame = Frame(self.master, width=500, height=400, bd=1)
        frame.pack()

        frameAbout = Frame(frame, bd=0)
        message = "\nfabian (release 0.1) was brought to you by \n\n\
Henning O. Sorensen & Erik Knudsen\n\
Center for Fundamental Research: Metal Structures in Four Dimensions\n\
Risoe National Laboratory\n\
Frederiksborgvej 399\n\
DK-4000 Roskilde\n\
email: henning.sorensen@risoe.dk"

        Message(frameAbout, text=message,width=500).pack(fill=X, padx=5)
        frameAbout.pack(expand=1, pady=10, padx=5)

        frameAbout = Frame(frame, bd=0)
        Button(frameAbout,text='So what', bg='red', command=self.quit)\
                                          .pack(side=RIGHT)
        frameAbout.pack(expand=1, pady=10, padx=5)

    def quit(self):
        self.master.destroy()

def construct_filename(oldfilename,newfilenumber,padding=True):
  #some code to replace the filenumber in oldfilename with newfilenumber
  #by figuring out how the files are named
  import string
  p=re.compile(r"^(.*?)(-?[0-9]{0,4})(\D*)$")
  m=re.match(p,oldfilename)
  if padding==False:
    return m.group(1) + str(newfilenumber) + m.group(3)
  if m.group(2)!='':
    return m.group(1) + string.zfill(newfilenumber,len(m.group(2))) + m.group(3)# +'.' + m.group(4)
  else:
    return oldfilename

def deconstruct_filename(filename):
  p=re.compile(r"^(.*?)(-?[0-9]{0,4})(\D*)$")
  m=re.match(p,filename)
  if m==None or m.group(2)=='':
    number=0;
  else:
    number=int(m.group(2))
  ext=os.path.splitext(filename)
  filetype={'edf': 'edf',
    'gz': 'edf',
    'bz2': 'edf',
    'pnm' : 'pnm',
    'pgm' : 'pnm',
    'pbm' : 'pnm',
    'tif': 'tif',
    'tiff': 'tif',
    'img': 'adsc',
    'mccd': 'marccd',
    'sfrm': 'bruker100',
    m.group(2): 'bruker'
    }[ext[1][1:]]
  return (number,filetype)

def extract_filenumber(filename):
  return deconstruct_filename(filename)[0]

##########################
#   Main                 #
##########################
if __name__=='__main__':
  def start():
    import time
    t1=time.clock()
    if len(sys.argv) > 2:
      print "Only the first file will be opened"
    if len(sys.argv) >= 2:
      f=sys.argv[1]
    else:
      f=None
  
    root=Tk()
    mainwin = appWin(root,filename=f,zoomfactor=0.5,mainwin='yes')
    
    t2=time.clock()
    print "time:",t2-t1
    root.mainloop()
  start()
######## THE END ##############
#import profile
#profile.run('start()','profile_results')
#import pstats
#p=pstats.Stats('profile_results')
#p.sort_stats('cumulative').print_stats(40)
