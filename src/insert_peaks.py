#! /usr/bin/env python
"""

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:henning.sorensen@risoe.dk
"""
from fabio.file_series import filename_series

class readpeaksearch:
    """
    The useful class - called by the gui to process peaksearch output
    into spots
    """
    def __init__(self):
        self.lines=None
        self.peaks = []
 
    def readpeaks(self, peaksfilename, imagefile):
        """
        read in peaks found with peaksearch (ImageD11)
        """
        self.lines = open(peaksfilename,"r").readlines()
        self.images={}
        i=-1
        for line in self.lines:
            i+=1
            if line[0:6]=="# File":
                name = line.split()[-1]
                self.images[name]=i

        
        # stem, numb, filetype = deconstruct_filename(imagefile)
        fsobj =  filename_series(imagefile)
        start = self.images[imagefile]
        print imagefile
        try:
            end = self.images[fsobj.next()]
        except:
            end = len(self.lines)
            
        i = start +1
        line=self.lines[i]
        for line in self.lines[start:end]:
            if line[0]!='#' and len(line)>10:
                [npixels, yt, ypos, zpos] =  line.split()[0:4]
                self.peaks.append([npixels, ypos, zpos])

    def readallpeaks(self,peaksfilename):
        """
        read in peaks found with peaksearch (ImageD11)
        """
        self.lines = open(peaksfilename,"r").readlines()
        self.images={}
        name = 'None'
        for line in self.lines:
            if line[0:6] =="# File":
                if name != 'None': self.images[name]=self.peaks
                self.peaks = []
                name = line.split()[-1]
            elif line[0]!='#' and len(line)>10:
                    [npixels, yt, ypos, zpos] =  line.split()[0:4]
                    if npixels > 20:
                        self.peaks.append([npixels, ypos, zpos])
                    
        self.images[name]=self.peaks
                

        
if __name__=="__main__":
    import sys
    peaksearchfile = sys.argv[1]
    try:
        imagefile = sys.argv[2]
    except:
        pass
    peaklist = readpeaksearch()
    peaklist.readallpeaks(peaksearchfile)
    pickles = peaklist.images


    for k in pickles.keys():
        print k
