from Tkinter import Tk

class About:
    def __init__(self):
        self.master = Tk()
        self.master.title('About fabian')
        frame = Frame(self.master, width=500, height=400, bd=1)
        frame.pack()

        frameAbout = Frame(frame, bd=0)
        message = "\nfabian (RELEASE) was brought to you by \n\n\
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

