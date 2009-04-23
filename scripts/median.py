#!/usr/bin/env python
from Fabian.median import median_file_series
from optparse import OptionParser

if __name__=='__main__':


  def get_options():
    parser = OptionParser()
    parser.add_option("-i", "--filename", action="store",
                      dest="filename", type="string",
                      help="Name of an image file")
    parser.add_option("-o", "--output", action="store",
                      dest="median_filename", type="string",
                      default='median_image.edf',
                      help="Name of median file")
    parser.add_option("-f", "--first", action="store",
                      dest="first", type="int",
                      default = None,
                      help="first file in file series")
    parser.add_option("-l", "--length", action="store",
                      dest="filterlength", type="int",
                      default = None,
                      help="length of file series")
    parser.add_option("-s", "--step", action="store",
                      dest="delta", type="int",
                      default = 1,
                      help="step in between number of files to be used")
    parser.add_option("-d", "--debug", action="store_true",
                      dest="debug",default =False,
                      help="Run in debug mode")



    options , args = parser.parse_args()

    do_exit = False

    if options.filename == None:
      print "\nNo file name supplied [-i filename]\n"
      do_exit = True
    if options.first == None:
      print "\nThe number of the first image is missing [-f filenumber]\n"
      do_exit = True
    if options.filterlength == None:
      print "\nThe length of the file seris is missing [-l filelength]\n"
      do_exit = True
    if do_exit:
        parser.print_help()
        sys.exit()
    return options

  def start():
    import sys,os,time
    b=time.clock()
    mf=median_file_series(options.filename,
                          options.first,
                          options.filterlength,
                          options.delta,
                          options.debug)
    mf.run()
    mf.write(options.median_filename);
    mf.slide(2,
             options.delta)

    #mf.slide(int(sys.argv[3]),int(sys.argv[4]))
    #mf.write('med2.edf');
    #mf.slide(int(sys.argv[3]),int(sys.argv[4]))
    #mf.write('med3.edf');
    if options.debug:print 'process time (sec): ',(time.clock()-b)

  options = get_options()
  start()
    
