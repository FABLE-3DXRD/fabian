
from __future__ import absolute_import

import numpy as N
from OpenGL import GL
import sys
if sys.version_info[0] < 3:
    import Tkinter as oTk
else:
    import tkinter as oTk
from pyopengltk import Opengl



class ReliefPlot:
    def __init__(self,master,newimage=None,corners=[0,0,0,0]):
        self.master = master
        self.f=oTk.Frame(self.master)
        self.f.pack(side=oTk.BOTTOM,expand=oTk.NO,fill=oTk.X)
        self.dataoff=0
        self.corners = corners
        data = list(newimage.crop(self.corners).getdata())
        extrema = [min(data),max(data)]
        self.extrema = extrema
        data = N.reshape( data,[self.corners[3]-self.corners[1], self.corners[2]-self.corners[0]])
        self.map=data.copy()
        self.pointsize=4.

        self.map = N.transpose(self.map)
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
        self.reliefWin = Opengl(self.f,width = 500, height = 500 )#, double = 1)
        self.reliefWin.redraw = self.array_redraw
        self.reliefWin.autospin_allowed = 1
        self.reliefWin.fovy=5
        self.reliefWin.near=1e2
        self.reliefWin.far=1e-6
        import math
        self.reliefWin.pack(side = oTk.TOP, expand = oTk.YES, fill = oTk.BOTH)
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
        data = N.reshape( data,[self.corners[3]-self.corners[1], self.corners[2]-self.corners[0]])
        extrema = data.min(),data.max()
        self.map = data.copy()
        self.map = N.transpose(self.map)
        h = extrema[1]-extrema[0]
        if h != 0:
            self.zscale = self.size/(extrema[1]-extrema[0])
            self.map = self.map*self.zscale
        if self.sizex > self.sizey:
          self.scale = 0.75/self.sizex
        else:
          self.scale = 0.75/self.sizey
        self.zcenter = -(extrema[1]+extrema[0])*self.zscale/2.0
        self.extrema = extrema
        self.reliefWin.tkRedraw() # Redraw canvas
        

    def array_redraw(self,reliefWin):
         # go a bit faster ? 
         GL.glClearColor(0., 0., 0., 0)
         GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
         GL.glOrtho(-1,1,-1,1,-1,1)
         GL.glDisable(GL.GL_LIGHTING)
         GL.glColor3f(1.0, 1.0, 1.0) # white
         GL.glPointSize(self.pointsize)
         GL.glPushMatrix()
         GL.glScalef(self.scale,self.scale,self.scale)
         GL.glRotate(-20,0,0,1)
         GL.glRotate(-110,1,0,0)
         GL.glTranslatef(-self.sizex/2.0,-self.sizey/2.0,self.zcenter)
         GL.glEnableClientState( GL.GL_VERTEX_ARRAY )
         GL.glEnableClientState( GL.GL_COLOR_ARRAY )
         xyz = N.zeros( (self.sizey,3), N.float32)
         xyz[:,0] = range(self.sizey)
         c = N.zeros( (self.sizey,3), N.float32)
         s = self.zscale*(self.extrema[1] - self.extrema[0])
         l = self.zscale*self.extrema[0]
         h = self.zscale*self.extrema[1]
         for i in range(self.sizex):
             xyz[:,1] = i
             xyz[:,2] = self.map[i]
             c[:,0] = (self.map[i]-l)/s
             c[:,1] = (self.map[i]-l)/s
             c[:,2] = (h-self.map[i]-l)/s
             GL.glVertexPointer( 3, GL.GL_FLOAT, 0, xyz.tostring() )
             GL.glColorPointer( 3,  GL.GL_FLOAT, 0, c.tostring() )
             GL.glDrawArrays( GL.GL_LINE_STRIP, 0, self.sizey )
         xyz = N.zeros( (self.sizex, 3), N.float32)
         c = N.zeros( (self.sizex,3), N.float32)
         xyz[:,1] = range(self.sizex)
         for i in range(self.sizey):
             xyz[:,0] = i
             xyz[:,2] = self.map[:,i]
             c[:,0] = (self.map[:,i]-l)/s
             c[:,1] = (self.map[:,i]-l)/s
             c[:,2] = (h-self.map[:,i]-l)/s
             GL.glVertexPointer( 3, GL.GL_FLOAT, 0, xyz.tostring() )
             GL.glColorPointer( 3,  GL.GL_FLOAT, 0, c.tostring() )
             GL.glDrawArrays( GL.GL_LINE_STRIP, 0, self.sizex )
         GL.glEnable(GL.GL_LIGHTING)
         GL.glPopMatrix()

