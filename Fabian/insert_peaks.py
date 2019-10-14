#! /usr/bin/env python
"""

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:henning.sorensen@risoe.dk
"""
from __future__ import absolute_import
from __future__ import print_function
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
        try:
            end = self.images[next(fsobj)]
        except:
            end = len(self.lines)
            
        i = start +1
        line=self.lines[i]
        for line in self.lines[start:end]:
            if line[0]!='#' and len(line)>10:
                try:
                    [npixels, yt, ypos, zpos] =  line.split()[0:4]
                    npixels = int(npixels)
                    ypos = float(ypos)
                    zpos = float(zpos)
                    self.peaks.append([npixels, ypos, zpos])
                except:
                    pass

    def readallpeaks(self,peaksfilename):
        """
        read in peaks found with peaksearch (ImageD11)
        """
        import os,fabio
        self.lines = open(peaksfilename,"r").readlines()
        self.images={}
        name = 'None'
        for line in self.lines:
            if line[0:6] =="# File":
                if name != 'None': self.images[name]=self.peaks
                self.peaks = []
                # key to name, not number
                name =  os.path.split(line.split()[-1])[-1]
                if name[-1] == "]": # frame number
                    name = name.split("[")[0]
            elif line[0]!='#' and len(line)>10:
                try:
                    [npixels, yt, ypos, zpos] =  line.split()[0:4]
                    npixels = int(npixels)
                    ypos = float(ypos)
                    zpos = float(zpos)
                    if npixels > 0:
                        self.peaks.append([npixels, ypos, zpos])
                except:
                    pass
        self.images[name]=self.peaks
        
    def readallpeaks_flt(self,peaksfilename):
        """
        read in flt peaks found with peaksearch (ImageD11)
        """
        import os,fabio
        self.lines = open(peaksfilename,"r").readlines()
        try:
            from ImageD11 import columnfile
        except:
            return False
        cf = columnfile.columnfile(peaksfilename)
        self.images = cf
        return 

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
        print(k)
