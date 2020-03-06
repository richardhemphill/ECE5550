#==============================================================================
# File: PitchDeterminationAlgorithm.py
# Author: Richard Hemphill
# ID: 903877709
# Class: ECE5550 High Performance Computing
# Teacher: Dr. Venton Kepuska
# Project: Perform sound analysis with ability to utilize GPU or CPU for 
#   processing. There are 3 plots (magnitude, frequency, pitch).  The data
#   comes from either sound file or microphone.  The window provides a GUI with
#   command buttons for easier control.  An elapsed time is displayed for the 
#   user to demonstrate GPU vs CPU performance.
#==============================================================================

#import time
#from time import process_time
#import importlib
from tkinter import *
#from tkinter import messagebox
from tkinter.filedialog import askopenfilename
#import amfm_decompy.pYAAPT as pYAAPT
#import amfm_decompy.basic_tools as basic
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
#import matplotlib.pyplot as pplt 
#import numpy as np
#import wave
#import sys
#import os
#import pyaudio

## Class containing functionality needed for Pitch Determination Algorithm
class PitchDeterminationAlgorithm(object):

    # Public PitchDeterminationAlgorithm Members

    ## Constructor
    def __init__(self):
        self.gui=PitchDeterminationAlgorithm.GUI()

    ## Starts the Pitch Determination Algorithm
    def run(self):
        self.gui.run()

    #####################
    ### Inner Classes ###
    #####################

    ### GUI Classes ###

    ## Class that sets up and manages the graphical interface.
    class GUI(object):
        # Constants
        PDA_TITLE="Pitch Determination Algorithm"   # window title
        WINDOW_PERCENT_SCREEN=0.75                  # use 75% screen width and height

        # Public GUI Members

        ## Constructor
        def __init__(self):
            self.window=Tk()
            self.__configureWindow(self.window)
            self.commandForm=PitchDeterminationAlgorithm.CommandForm(self.window)
            self.pdaPlots=PitchDeterminationAlgorithm.PdaPlots(self.window)

        ## Activates the GUI
        def run(self):
            self.window.mainloop()

        # Private GUI Members

        ## Initializes the look of the GUI
        def __configureWindow(self, window):
            window.geometry(self.__windowSize(window))
            window.resizable(width=True, height=True)
            window.title(self.PDA_TITLE)

        ## Determines the size the GUI window
        def __windowSize(self,window):
            # get screen size
            screenWidth=window.winfo_screenwidth()
            screenHeight=window.winfo_screenheight()

            # set window size to be within screen
            windowWidth=int(screenWidth*self.WINDOW_PERCENT_SCREEN)
            windowHeight=int(screenHeight*self.WINDOW_PERCENT_SCREEN)

            # format to string that for geometry call
            return "{}x{}".format(windowWidth,windowHeight)

    ## GUI Controls ##

    ## Class that manages the window form for controlling the GUI.
    class CommandForm(object):

        ## Constructor
        def __init__(self, window):
            self.frame=Frame(window)
            self.processorSwitch = PitchDeterminationAlgorithm.ProcessorSwitch(self.frame)
            self.sourceSwitch = PitchDeterminationAlgorithm.SourceSwitch(self.frame)
            self.fileBrowser = PitchDeterminationAlgorithm.FileBrowser(self.frame)
            self.frame.pack(anchor=N, fill=X, expand=YES)

    ## Genralized class for toggle switched in the GUI.
    class CommandSwitch(object):
        DEFAULT_MODE=1              # default to GPU mode

        ## Constructor
        def __init__(self, form, modes, default=DEFAULT_MODE, color=None):
           self.frame=Frame(form)
           self.switch = IntVar(form,self.DEFAULT_MODE)
           for (text, mode) in modes.items():           # itterate thru modes
                r = Radiobutton(master=self.frame)      # parent widget
                r.config(text=text)                     # button display text
                r.config(variable=self.switch)          # switch variable
                r.config(value=mode)                    # value of switch
                r.config(indicatoron=False)             # raised/sunken button
                if color is not None: r.config(background=color) # set color
                r.pack(side=LEFT)                       # next left within parent widget
           self.frame.pack(side=LEFT, padx=10)

    ## Class for toggling between which type of process will handle calculations.
    class ProcessorSwitch(CommandSwitch):
        MODES={"GPU":1,"CPU":2}
        DEFAULT_MODE=1              # default to GPU mode
        SWITCH_COLOR='light blue'

        ## Constructor
        def __init__(self, form):
            super().__init__(form=form, modes=self.MODES, default=self.DEFAULT_MODE, color=self.SWITCH_COLOR)

    ## Class for toggling between source for auditory data.
    class SourceSwitch(CommandSwitch):
        MODES={"MIC":1,"FILE":2}
        DEFAULT_MODE=2              # default to File mode
        SWITCH_COLOR='pink'

        ## Constructor
        def __init__(self, form):
            super().__init__(form=form, modes=self.MODES, default=self.DEFAULT_MODE, color=self.SWITCH_COLOR)

    ## Class for selecting sound file.
    class FileBrowser(object):

        # Public FileBrowser Members

        ## Constructor
        def __init__(self, form):
            self.frame=Frame(form)
            self.srcFile=StringVar()
            self.prevSrcFile=None
            self.entry=Entry(self.frame, textvariable=self.srcFile, justify=LEFT)
            self.entry.bind("<Return>", self.__OnFileEntryClick)
            self.entry.pack(side=LEFT, fill=X, expand=YES)
            self.button=Button(self.frame, text="Browse", command=lambda:self.__loadFile())
            self.button.pack(side=LEFT)
            self.frame.pack(side=LEFT, padx=10, fill=X, expand=YES)

        # Private FileBrowser Members

        ## Open dialog window for finding/select file.
        def __loadFile(self):
            fileName=askopenfilename(title = "Select sound file",
                filetypes = (("Wave files","*.wav"), 
                             ("MP3 files","*.mp3")))
            self.srcFile.set(fileName)
            self.srcMode.set(self.INPUT_SOURCES.get('FILE'))
            #self.processSignals()

        ## 
        def __OnFileEntryClick(self, event):
            value=self.srcFile.get().strip()
            changed = True if self.prevSrcFile != value else False
            if changed:
                self.srcMode.set(self.INPUT_SOURCES.get('FILE'))
                #self.processSignals()
            self.prevSrcFile=value

    class MagnitudePlot(object):
        XLABEL_STR = 'Samples'
        YLABEL_STR = 'Magnitude'
        LABEL_FONTSIZE = 12

        def __init__(self, plt):
            self.plt = plt.add_subplot(311)
            self.plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)

        def update(self, data):
            self.data = data

        def display(self):
            self.plt.clear()
            self.plt.plot(self.data)
            self.plt.axis([0,len(data),-2**16/2,2**16/2])

    class FrequencyPlot(object):
        XLABEL_STR = 'Time'
        YLABEL_STR = 'Frequency (Hz)'
        LABEL_FONTSIZE = 12
        AUTOSCALE_ENABLE = True
        AUTOSCALE_AXIS = 'x'
        AUTOSCALE_TIGHT = True

        def __init__(self, plt, rate=44100, nttf=1024, noverlap=900, cmap='gray_r'):
            self.plt = plt.add_subplot(312)
            self.plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.rate = rate
            self.nttf = nttf
            self.noverlap = noverlap
            self.cmap = cmap

        def update(self, data):
            self.data = data

        def display(self):
            self.plt.specgram(self.data, NFFT=self.nttf, Fs=self.rate, noverlap=self.noverlap, cmap=self.cmap)
            self.plt.autoscale(enable=self.AUTOSCALE_ENABLE, axis=self.AUTOSCALE_AXIS, tight=self.AUTOSCALE_TIGHT)

    class PitchPlot(object):
        XLABEL_STR = 'Samples'
        YLABEL_STR = 'Pitch (Hz)'
        LABEL_FONTSIZE = 12
        PITCH_LABEL = 'pitch interpolation'
        PITCH_COLOR = 'green'
        STEP_LABEL = 'step interpolation'
        STEP_COLOR = 'blue'
        SPLINE_LABEL = 'spline interpolation'
        SPLINE_COLOR = 'red'
        LEGEND_LOC = 'upper right'
        AUTOSCALE_ENABLE = True
        AUTOSCALE_AXIS = 'x'
        AUTOSCALE_TIGHT = True

        def __init__(self, plt, rate=44100):
            self.plt = plt.add_subplot(313)
            self.plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.rate = rate

        def update(self, data):
            basicSignal = basic.SignalObj(data, self.rate)
            self.pitch = pitch = pYAAPT.yaapt(basicSignal)
            self.pitchStep = pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='step')
            self.pitchSpline = pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='spline')

        def display(self):
            self.plt.clear()
            self.plt.plot(self.pitch.values, label=self.PITCH_LABEL, color=self.PITCH_COLOR)
            self.plt.plot(self.pitchStep.values, label=self.STEP_LABEL, color=self.STEP_COLOR)
            self.plt.plot(self.pitchSpline.values, label=self.SPLINE_LABEL, color=self.SPLINE_COLOR)
            self.plt.legend(loc=self.LEGEND_LOC)
            self.plt.grid
            self.plt.axes.set_ylim([0,1000])
            self.plt.autoscale(enable=self.AUTOSCALE_ENABLE, axis=self.AUTOSCALE_AXIS, tight=self.AUTOSCALE_TIGHT)

    class PdaPlots:
        TITLE_STR = 'Signal'
        TITLE_FONTSIZE = 14

        def __init__(self, win):
            self.frame = Frame(win)
            self.frame.pack(anchor=CENTER, fill=BOTH, expand=YES)
            self.plt=Figure()
            self.plt.suptitle(self.TITLE_STR, fontsize=self.TITLE_FONTSIZE)
            self.subPlots = list()
            self.mPlt = PitchDeterminationAlgorithm.MagnitudePlot(self.plt)
            self.subPlots.append(self.mPlt)
            self.fPlt = PitchDeterminationAlgorithm.FrequencyPlot(self.plt)
            self.subPlots.append(self.fPlt)
            self.pPlt = PitchDeterminationAlgorithm.PitchPlot(self.plt)
            self.subPlots.append(self.pPlt)
            self.canvas = FigureCanvasTkAgg(self.plt, master=self.frame)

        def update(self,data):
            for plt in self.subPlots:
                plt.update(data)

        def display(self):
            for plt in self.subPlots:
                plt.diplay()

    class CpuPlots(PdaPlots):
        def __init__(self, frame):
            super(PitchDeterminationAlgorithm.CpuPlots,self).__init__(frame)

    class GpuPlots(PdaPlots):
        def __init__(self, frame):
            super(PitchDeterminationAlgorithm.GpuPlots,self).__init__(frame)

    ### Processing Classes ###

    ## Class to handle pitch processing
    #  This is a sigleton so that only one instance keeps processed data
    class PitchProcessor(object):
        __instance = None

        ## Creates new object
        def __new__(cls):
            if cls.__instance is None:
                cls.__instance = super(PitchProcessor, cls).__new__(cls)
            return cls.__instance

###################################
### Designated Start of Program ###
###################################
if __name__ == '__main__':
    pda = PitchDeterminationAlgorithm()     # instantiate PDA object
    pda.run()                               # activate PDA object