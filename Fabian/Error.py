from __future__ import absolute_import
try:
    from Tkinter import *
except:
    from tkinter import *
import time

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
        
    def Er2(self,message):
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

    def sleep(self,howlong):
        time.sleep(howlong)

    def quit(self):
        self.master.destroy()


