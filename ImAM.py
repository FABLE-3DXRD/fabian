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
import  Numeric
import sys
import edfimage, tifimage, adscimage
from string import *
from PIL import Image, ImageTk, ImageFile, ImageStat
from tkFileDialog import *
import tkFont
import re
import os
import time

class ImAMImage(Image.Image):
  def __init__(self):
    Image.Image.__init__(self)
    self.minval=0
    self.maxval=0
    self.meanval=0
    self.stddev=0
    
class imageWin:
  def __init__(self,master,fileprefix=None,filenumber=0,title=None,zoomfactor=1,mainwin='no',zoomable='yes',coords=[0,0,0,0],image=None):
    #initialize var
    self.master=master
    #these keep track of the AOIs
    self.aoi={}
    self.no_win = 0
    self.scale=0
    self.offset=0
    self.transientaoi=None
    self.maxval=StringVar()
    self.minval=StringVar()
    master.bind('q',self.quit)
    master.bind('<FocusIn>',self.MouseEntry)
    
    if title: self.master.title(title)
    
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
    frameImage = Frame(container, bd=0, bg="white")
    self.canvas_xsize = int(self.xsize*self.zoomfactor)
    self.canvas_ysize = int(self.ysize*self.zoomfactor)
    self.canvas = Canvas(frameImage, width=self.canvas_xsize, height=self.canvas_ysize)
    self.canvas.pack(side=TOP,fill=BOTH, expand='yes')
    frameImage.pack(side=TOP,expand=1, pady=10, padx=5)
    #bind events
    self.canvas.bind('<Button-3>', self.Mouse3Press)
    self.canvas.bind('<Button3-Motion>', self.Mouse3PressMotion)
    self.canvas.bind('<Button3-ButtonRelease>', self.Mouse3Release)
    self.canvas.bind('<Motion>', self.MouseMotion)
    #New bindings for Relief plot
    self.canvas.bind('<Control-Button-3>', self.Mouse3Press)
    self.canvas.bind('<Control-Button3-Motion>', self.Mouse3PressMotion)
    self.canvas.bind('<Control-Button3-ButtonRelease>', self.CtrlMouse3Release)
    
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
 
  def Mouse3Press(self, event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasx(event.y)
    if self.val_canvas_coord((x,y)):
      self.transientcorners=[x,y,x,y]
    self.drawAoi()

  def Mouse3PressMotion(self, event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasy(event.y)
    if self.val_canvas_coord((x,y)):
      self.transientcorners[2:]=[x,y]
    self.drawAoi()

  def Mouse3Release(self, event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasy(event.y)
    if self.val_canvas_coord((x,y)):
      self.transientcorners[2:]=[x,y]
    self.drawAoi(transient=0)

  def CtrlMouse3Release(self, event):
    x=self.canvas.canvasx(event.x)
    y=self.canvas.canvasy(event.y)
    if self.val_canvas_coord((x,y)):
      self.transientcorners[2:]=[x,y]
    self.drawAoi(transient=2)

  def MouseEntry(self,event):
    #mouse has entered the window - check for nonexistent children
    children=self.master.winfo_children()
    for k in self.aoi.keys():
      w=self.aoi[k]
      if not w['zoomwin'].master in children:
        self.canvas.delete(w['aoi'])
        self.aoi.pop(k)
 
  def val_canvas_coord(self,c):
    if c[0]<0 or c[0]>self.canvas_xsize or c[1]<0 or c[1]>self.canvas_ysize:
      return False
    else:
      return True

  def drawAoi(self,transient=1,fix=0):
    if self.transientaoi:
      self.canvas.delete(self.transientaoi)#the last element of the list is the one to be redrawn. 
    if transient==1:
      r=self.canvas.create_rectangle(self.transientcorners,outline='RoyalBlue')
      self.transientaoi=r
    elif transient==2:
      if 'zoom' in self.master.wm_title():
        t= 'relief of ' + self.master.wm_title()
      else:
	t='relief of main'
      #tag the rectangle for later reference
      r=self.canvas.create_rectangle(self.transientcorners,outline='LimeGreen',tag=t)
      self.aoi[t]={'coords': self.transientcorners, 'aoi':r, 'zoomwin': self.openrelief(t)}
      #self.openrelief(t)
    else:
      if 'zoom' in self.master.wm_title():
	t= self.master.wm_title() +'.%d' % len(self.aoi)
      else:
	t='zoom %d'% len(self.aoi)
      #tag the rectangle for later reference
      r=self.canvas.create_rectangle(self.transientcorners,outline='red',tag=t)
      self.aoi[t]={'coords': self.transientcorners, 'aoi':r, 'zoomwin': self.openzoom(t)}
      self.update()

  def openzoom(self,tag):
    w=Toplevel(self.master)
    t=self.transientcorners
    corners=[int(self.zoomarea[0]+t[0]/self.zoomfactor), int(self.zoomarea[1]+t[1]/self.zoomfactor), int(self.zoomarea[0]+t[2]/self.zoomfactor), int(self.zoomarea[1]+t[3]/self.zoomfactor)]
    newwin=imageWin(w,title=tag,fileprefix=None,zoomfactor=self.zoomfactor*4,coords=corners,image=self.im)
    return newwin

  def openrelief(self,tag):
      # Make 3D relief window
      t=self.transientcorners
      corners=[int(self.zoomarea[0]+t[0]/self.zoomfactor), int(self.zoomarea[1]+t[1]/self.zoomfactor), int(self.zoomarea[0]+t[2]/self.zoomfactor), int(self.zoomarea[1]+t[3]/self.zoomfactor)]
      
      self.reliefmap = list(self.im.crop(corners).getdata())
      self.reliefextrema = [min(self.reliefmap),max(self.reliefmap)]
      print self.reliefextrema
      self.reliefmap = Numeric.reshape( self.reliefmap,[corners[3]-corners[1], corners[2]-corners[0]])
      reli=Toplevel(self.master)
      reli.title(tag)
      newReli=ReliefPlot(reli,data=self.reliefmap,extrema=self.reliefextrema)
      return newReli
    
  def update(self,scaled_min=0,scaled_max=0,newimage=None):
    if self.scale==0:
      self.reset_scale()
    #scale this instance itself and all its children
    if (scaled_min,scaled_max,newimage)==(atof(self.minval.get()),atof(self.maxval.get()),None):
      return True
    elif (scaled_min==scaled_max==0):
      scaled_min = atof(self.minval.get())
      scaled_max = atof(self.maxval.get())
    else:
      self.minval.set(scaled_min)
      self.maxval.set(scaled_max)
    self.maxval.set(scaled_max)
    self.scale = 255.0 / (scaled_max - scaled_min)
    self.offset = - scaled_min * self.scale
    
    if newimage: self.im=newimage
    
    # scale convert from 16bit to 8bit for Tkinter
    if self.zoomarea[2]!=self.xsize and self.zoomarea[3]!=self.ysize:
      self.imcrop = self.im.crop(self.zoomarea)
      self.im8c = self.imcrop.point(lambda i: i * self.scale + self.offset).convert('L')
      self.img = ImageTk.PhotoImage(self.im8c.resize((self.canvas_xsize,self.canvas_ysize)))
      self.im_min,self.im_max = self.imcrop.getextrema()
      l=list(self.imcrop.getdata())
      self.im_mean=sum(l)/len(l)
    else:
      #image should not be cropped
      self.im8c = self.im.point(lambda i: i * self.scale + self.offset).convert('L')
      self.img = ImageTk.PhotoImage(self.im8c.resize((self.canvas_xsize,self.canvas_ysize)))
      self.im_min,self.im_max = self.im.getextrema()
      if self.im.meanval:
	self.im_mean=self.im.meanval
      else:
	self.im_mean=-1
    self.ShowMin.config(text="Min %i" %(self.im_min))
    self.ShowMax.config(text="Max %i" %(self.im_max))
    self.ShowMean.config(text="Mean %i" %(self.im_mean))
    self.currentImage = self.canvas.create_image(0,0,anchor=NW, image=self.img)
    self.canvas.lower(self.currentImage)
    #update children
    self.children = self.master.winfo_children()
    for k in self.aoi.keys():
      w=self.aoi[k]
      w['zoomwin'].update(scaled_min,scaled_max,newimage=newimage)
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
    scaled_max = ((self.im_max - self.im_min)/255 *i)+self.im_min
    self.maxval.set("%.0f"%scaled_max)

  def quit(self,event=None):
    self.master.destroy()

class appWin(imageWin):
  def __init__(self,master,fileprefix=None,filenumber=0,filename=None,filetype=None,zoomfactor=1,mainwin='no',zoomable='yes',coords=[0,0,0,0],image=None):
    #initialize var
    self.master=master
    #these keep track of the AOIs
    self.aoi={}
    self.no_win = 0
    self.scale=0
    self.offset=0
    self.transientaoi=None
    self.maxval=StringVar()
    self.minval=StringVar()
    self.displaynumber=StringVar()
    self.filename=StringVar()
    self.filetype = filetype
    master.bind('q',self.quit)
    master.bind('<FocusIn>',self.MouseEntry)

    if filename:
      self.filename.set(filename)
      self.displaynumber.set(extract_filenumber(filename))
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
    if self.ysize > 1560:
      self.zoomfactor = 0.25
    elif self.ysize > 768:
      self.zoomfactor = 0.5
    else:
      self.zoomfactor = 1
    
    frame = Frame(master, bd=0, bg="white") #, width=600, height=600) 
    frame.pack(fill=X)

    #add menubar
    self.make_command_menu(frame)
    #Add Notebook tabs
    self.noteb1 = Pmw.NoteBook(frame)
    self.noteb1.pack(fill='both')
    self.page1 = self.noteb1.add('Image')
    self.page2 = self.noteb1.add('Info')
    
    #call __init__ in the parent class
    self.make_scaling_ctls(self.page1)
    
    self.make_image_canvas(self.page1)
    #imageWin.__init__(self,master,page1,fileprefix=fileprefix,filenumber=filenumber,zoomfactor=self.zoomfactor,coords=(0,0,self.xsize,self.ysize),image=self.im)
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

  def make_header_page(self):
      self.headcheck=[]
      print self.headcheck
      self.headtext={}
      self.newitem={}
      for self.item in self.im.header:
        self.fm = Frame(self.HeaderInterior)
        self.newitem[self.item]=StringVar()
        self.headcheck.append(Checkbutton(self.fm,text='%s' %(self.item), command=self.update_header_label,variable=self.newitem[self.item], bg='white',anchor=W,width=20).pack(side=LEFT,anchor=W))
        self.headtext[self.item]= Label(self.fm,text='%s' %(self.im.header[self.item]), bg='white',anchor=W,width=100)
        self.headtext[self.item].pack(side=LEFT,fill=X,expand='yes')
        self.fm.pack(side=TOP,anchor=W)


  def make_header_info(self):
    self.HeaderInfo = Label(self.page1, text='', anchor=W)
    self.HeaderInfo.pack(side=TOP,fill=BOTH)
  
  def update_header_page(self):
      for item in self.im.header:
        self.headtext[item].config(text='%s' %(self.im.header[item]))

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
    e.bind('<FocusOut>',self.rescale)
    e.bind('<Return>',self.rescale)
    e.bind('<KP_Enter>',self.rescale)
    e.pack(side=LEFT,padx=4)
    Label(frameScale,text='max:', bg='white').pack(side=LEFT)
    e=Entry(frameScale, textvariable=self.maxval, bg='white', width=6)
    e.bind('<FocusOut>',self.rescale)
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
    CmdBtn = Menubutton(frameMenubar, text='File',underline=0)
    CmdBtn.pack(side=LEFT, padx="2m")
    CmdBtn.menu =Menu(CmdBtn)
    CmdBtn.menu.add_command(label='Open',command=self.OpenFile)
    #CmdBtn.menu.add_command(label='Close')
    #CmdBtn.menu.entryconfig(0,state=DISABLED)
    CmdBtn.menu.add_command(label='Exit',command=self.quit)
    CmdBtn['menu']=CmdBtn.menu
    CmdBtn2 = Menubutton(frameMenubar, text='Help',underline=0)
    CmdBtn2.pack(side=LEFT, padx="2m")
    CmdBtn2.menu =Menu(CmdBtn2)
    CmdBtn2.menu.add_command(label='About',command=self.about)
    CmdBtn2['menu']=CmdBtn2.menu
    #return CmdBtn, CmdBtn2
    frameMenubar.pack(fill=X,side=TOP)
    frameMenubar.tk_menuBar((CmdBtn, CmdBtn2))

  def OpenFile(self,filename=True):
    self.filename.set(askopenfilename(filetypes=[("EDF files", "*.edf"),("Tif files", "*.tif"),("ADSC files", "*.img"),("All Files", "*")]))
    (self.fileprefix,newfilenumber,self.filetype)=split_filename(self.filename.get())
    self.displaynumber.set(newfilenumber)
    if filename == None: # No image has been opened before
      return 
    else:
      self.make_header_page()
      self.gotoimage()
  
  def rescale(self,event=None):
    self.update()
    return True

  def scaleimage___(self,scaled_min=0,scaled_max=0):
    #obsolete
    if self.scale==0:
      self.reset_scale()
    #scale this instance itself and all its children
    if (scaled_min==scaled_max==0):
      scaled_min = atof(self.minval.get())
      scaled_max = atof(self.maxval.get())
    else:
      self.minval.set(scaled_min)
      self.maxval.set(scaled_max)
    self.maxval.set(scaled_max)
    self.scale = 255.0 / (scaled_max - scaled_min)
    self.offset = - scaled_min * self.scale
   
    #scale children
    self.children = self.master.winfo_children()
    for k in self.aoi.keys():
      w=self.aoi[k]
      print "We are updating zoom", k,w
      w['zoomwin'].scaleimage___(scaled_min,scaled_max)
    
  
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
    self.update(newimage=self.im)
    self.update_header_page()
    self.update_header_label()
    self.filename.set(newfilename)
    self.displaynumber.set(newfilenumber)
    return True

  def nextimage(self):
    #update filename, prefix and number
    newfilenumber=int(self.displaynumber.get())+1
    newfilename=construct_filename(self.filename.get(),newfilenumber)
    #self.filename.set("%s%0.4d.%s"%((self.fileprefix,newfilenumber,self.filetype)))
    try:
      self.openimage(newfilename)#try to open that file
    except IOError:
      e=Error()
      msg="No such file: %s " %(newfilename)
      e.Er(msg)
      return False
    #image loaded ok
    self.update(newimage=self.im)
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
    self.update(newimage=self.im)
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
    
    #if filetype in ('edf',tif,'img'):
    img=eval( filetype+'image.'+filetype+'image()')
    print img
    try:
      self.im=img.read(filename).toPIL16()
      (self.im.minval,self.im.maxval,self.im.meanval)=(img.getmin(),img.getmax(),img.getmean())
      self.im.header=img.getheader()
      (self.xsize, self.ysize)=(img.dim1, img.dim2)
    except IOError:
      raise
    self.zoomarea=[0,0,self.xsize,self.ysize]
    self.master.title("ImAM - %s" %(filename))

      
  def about(self):
    About()
    
#  def quit(self):
#    self.master.destroy()

class ReliefPlot:
    def __init__(self,master,data=None,extrema=None):
        import OpenGL.GL as GL
        import OpenGL.Tk as oTk
        self.master = master
        print master
	self.f=oTk.Frame(self.master)
        self.f.pack(side=oTk.BOTTOM,expand=oTk.NO,fill=oTk.X)
        self.dataoff=0
        if data!=None:
            self.map=data.copy()
        else:
            self.map=Numeric.array([0,0,0])
        self.pointsize=4.
        self.map = Numeric.transpose(self.map)
        self.sizex = self.map.shape[0]
        self.sizey = self.map.shape[1]
        print self.map.shape
        self.size = (self.sizex+ self.sizey)/2.0
        self.scale = self.size/(extrema[1]-extrema[0])
        self.map = self.map*self.scale
        self.o = oTk.Opengl(self.f,width = 500, height = 500, double = 1)
        self.o.redraw = self.redraw
        self.o.autospin_allowed = 1
        if self.sizex > self.sizey:
          self.o.set_eyepoint(13.*self.sizex)
        else:
          self.o.set_eyepoint(13.*self.sizey)
        self.zcenter = -(extrema[1]+extrema[0])*self.scale/2.0
        self.o.fovy=5
        self.o.near=1e2
        self.o.far=1e-6
        import math
        self.o.pack(side = oTk.TOP, expand = oTk.YES, fill = oTk.BOTH)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        oTk.Button(self.f,text="Help",command=self.o.help).pack(side=oTk.LEFT)
        oTk.Button(self.f,text="Reset",command=self.o.reset).pack(side=oTk.LEFT)
        oTk.Button(self.f,text="Quit",command=self.quit).pack(side=oTk.RIGHT)

    def quit(self):
        self.master.destroy()
    
    def update(self,whatever,whoever,newimage=None):
	pass
    
    def redraw(self,o):
         import OpenGL.GL as GL
         GL.glClearColor(0., 0., 0., 0)
         GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
         GL.glOrtho(-1,1,-1,1,-1,1)
         GL.glDisable(GL.GL_LIGHTING)
         GL.glColor3f(1.0, 1.0, 1.0) # white
         GL.glPointSize(self.pointsize)
         GL.glPushMatrix()
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
        self.master.title('About ImAM')
        frame = Frame(self.master, width=500, height=400, bd=1)
        frame.pack()

        frameAbout = Frame(frame, bd=0)
	message = "\nImAM (Image Analysis Module) was brought to you by \n\n\
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
 
def split_filename(filename):
    m=re.match(r"(.+?)([0-9]{0,4})\.((edf|tif|img))$",filename)
    if m.group(2):
      return (m.group(1),int(m.group(2)),m.group(3))
    else:
      return (m.group(1),0,m.group(3))

def construct_filename_pattern():
  pass

def construct_filename(oldfilename,newfilenumber,padding=True):
  #some code to replace the filenumber in oldfilename with newfilenumber
  #by figuring out how the files are named
  import string
  #p=re.compile(r"^(.*?)(-?[0-9]{0,4})(\D*)\.(.+)$")
  p=re.compile(r"^(.*?)(-?[0-9]{0,4})(\D*)$")
  m=re.match(p,oldfilename)
  #print m.group(1),m.group(2),m.group(3)
  if padding==False:
    return m.group(1) + str(newfilenumber) + m.group(3)
  if m.group(2)!='':
    return m.group(1) + string.zfill(newfilenumber,len(m.group(2))) + m.group(3)# +'.' + m.group(4)
  else:
    return oldfilename

def extract_filenumber(filename):
  #p=re.compile(r"^(.*?)(-?[0-9]{0,4})(\D*)\.(.+)$")
  p=re.compile(r"^(.*?)(-?[0-9]{0,4})(\D*)$")
  m=re.match(p,filename)
  if m==None or m.group(2)=='':
    return 0;
  else:
    return int(m.group(2))

def join_filename(parts,oldfilename=None):
    import string
    m=re.match(r"(.+?)([0-9]{0,4})\.((edf|tif|img))$",oldfilename)
    print m.group(1),m.group(2),m.group(3)
    if m.group(2):
      return parts[0]+ string.zfill(parts[1],len(m.group(2))) + '.' + parts[2]
    else:
      return parts[0]+ '.' + parts[2]

##########################
#   Main                 #
##########################
if __name__=='__main__':
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
  sw = root.winfo_screenwidth()
  sh = root.winfo_screenheight()
  root.mainloop()
######## THE END ##############

