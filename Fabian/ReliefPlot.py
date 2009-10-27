import numpy as N

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
        data = N.reshape( data,[self.corners[3]-self.corners[1], self.corners[2]-self.corners[0]])
        self.map = data.copy()
        self.map = N.transpose(self.map)
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
         GL.glScalef(self.scale,self.scale,self.scale)
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

