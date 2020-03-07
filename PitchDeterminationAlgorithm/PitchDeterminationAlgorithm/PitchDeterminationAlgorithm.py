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
from enum import Enum

# Pattern Classes

class Singleton(type):
    def __init__(cls,name,bases,dic):
        super(Singleton,cls).__init__(name,bases,dic)
        cls.instance=None
    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance=super(Singleton,cls).__call__(*args,**kw)
        return cls.instance

## Class containing functionality needed for Pitch Determination Algorithm
class PitchDeterminationAlgorithm(object):

    # PitchDeterminationAlgorithm Enumerations

    class ProcessingModes(Enum):
        CPU  = 1
        GPU  = 2

    class InputSources(Enum):
        FILE = 1
        MIC  = 2

    # Public PitchDeterminationAlgorithm Members

    ## Constructor
    def __init__(self):
        self.__gui=PitchDeterminationAlgorithm.GUI()

    ## Starts the Pitch Determination Algorithm
    def run(self):
        self.__gui.run()

    #####################
    ### Inner Classes ###
    #####################

    ### GUI Classes ###

    ## Class that sets up and manages the graphical interface.
    class GUI(object):
        # Constants
        TITLE='Pitch Determination Algorithm'   # window title
        SCREEN_PERCENT=0.75                     # use 75% screen width and height

        # Public GUI Methods

        ## Constructor
        def __init__(self):
            self.__window=Tk()
            self.__configureWindow()
            self.__commandForm=PitchDeterminationAlgorithm.CommandForm(self.__window)
            self.__pdaPlots=PitchDeterminationAlgorithm.PdaPlots(self.__window)

        ## Activates the GUI
        def run(self):
            self.__window.mainloop()

        # Private GUI Members

        ## Initializes the look of the GUI
        def __configureWindow(self):
            self.__window.geometry(self.__windowSize())
            self.__window.resizable(width=True, height=True)
            self.__window.title(self.TITLE)

        ## Return geometry per the size the GUI window
        def __windowSize(self):
            # get screen size
            screenWidth=self.__window.winfo_screenwidth()
            screenHeight=self.__window.winfo_screenheight()

            # set window size to be within screen
            windowWidth=int(screenWidth*self.SCREEN_PERCENT)
            windowHeight=int(screenHeight*self.SCREEN_PERCENT)

            # format to string that for geometry call
            return "{}x{}".format(windowWidth,windowHeight)

    ## GUI Controls ##

    ## Class that manages the window form for controlling the GUI.
    class CommandForm(object):

        ## Constructor
        def __init__(self, window):
            self.__frame=Frame(window)
            self.__processorSwitch = PitchDeterminationAlgorithm.ProcessorSwitch(self.__frame)
            self.__sourceSwitch = PitchDeterminationAlgorithm.SourceSwitch(self.__frame)
            self.__fileBrowser = PitchDeterminationAlgorithm.FileBrowser(self.__frame)
            self.__frame.pack(anchor=N, fill=X, expand=YES)

    ## Genralized class for toggle switched in the GUI.
    class CommandSwitch(object, metaclass=Singleton):

        # Constants
        DEFAULT_COLOR='gray'
        DEFAULT_MODE=1

        ## Constructor
        def __init__(self, form, modes, color=None, default=DEFAULT_MODE):
            self.__frame=Frame(form)
            self.__mode = IntVar(form, default)
            for mode in modes:                           # itterate thru modes
                r = Radiobutton(master=self.__frame)    # parent widget
                r.config(text=mode.name)                # button display text
                r.config(variable=self.__mode)          # switch variable
                r.config(value=mode.value)              # value of switch
                r.config(indicatoron=False)             # raised/sunken button
                r.config(background=color)              # set color
                r.pack(side=LEFT)                       # next left in parent
            self.__frame.pack(side=LEFT, padx=10)

        @property
        def mode(self):
            return self.__mode

        @mode.setter
        def mode(self, value):
            self.__mode = value

    ## Class for toggling between which type of process will handle calculations.
    class ProcessorSwitch(CommandSwitch):
        COLOR='cornflower blue'

        ## Constructor
        def __init__(self, form):
            self.__modes=PitchDeterminationAlgorithm.ProcessingModes
            super().__init__(form=form, modes=self.__modes, color=self.COLOR)

    ## Class for toggling between source for auditory data.
    class SourceSwitch(CommandSwitch):
        COLOR='indian red'

        ## Constructor
        def __init__(self, form):
            self.__modes=PitchDeterminationAlgorithm.InputSources
            super().__init__(form=form, modes=self.__modes, color=self.COLOR)

    ## Class for selecting sound file.
    class FileBrowser(object):

        # Constants
        BUTTON_TEXT='Browse'
        OPEN_TITLE='Select sound file'
        FILE_TYPES=(("Wave files","*.wav"), 
                    ("MP3 files","*.mp3"))

        # Methods

        ## Constructor
        def __init__(self, form):
            self.__frame=Frame(form)
            self.__sourceSwitch=PitchDeterminationAlgorithm.SourceSwitch()
            self.__pitchTracker=PitchDeterminationAlgorithm.PitchTracker()
            self.__srcFile=StringVar()
            self.__prevSrcFile=None
            self.__entry=Entry(self.__frame, textvariable=self.__srcFile, justify=LEFT)
            self.__entry.bind("<Return>", self.__OnFileEntryClick)
            self.__entry.pack(side=LEFT, fill=X, expand=YES)
            self.__button=Button(self.__frame, text=self.BUTTON_TEXT, command=lambda:self.__loadFile())
            self.__button.pack(side=LEFT)
            self.__frame.pack(side=LEFT, padx=10, fill=X, expand=YES)

        ## Open dialog window for finding/select file.
        def __loadFile(self):
            fileName=askopenfilename(title = self.OPEN_TITLE, filetypes = self.FILE_TYPES)
            self.__srcFile.set(fileName)
            #self.__srcMode.set(PitchDeterminationAlgorithm.InputSources.FILE)
            #self.processSignals()
            self.__sourceSwitch.mode = PitchDeterminationAlgorithm.InputSources.FILE

        ## Action when files has been selected.
        def __OnFileEntryClick(self, event):
            value=self.__srcFile.get().strip()
            changed = True if self.__prevSrcFile != value else False
            if changed:
                self.__srcMode.set(PitchDeterminationAlgorithm.InputSources.FILE)
                #self.processSignals()
            self.__prevSrcFile=value

    class MagnitudePlot(object):
        XLABEL_STR = 'Samples'
        YLABEL_STR = 'Magnitude'
        LABEL_FONTSIZE = 12

        def __init__(self, plt):
            self.__plt = plt.add_subplot(311)
            self.__plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.__plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)

        def update(self, data):
            self.__data = data

        def display(self):
            self.__plt.clear()
            self.__plt.plot(self.__data)
            self.__plt.axis([0,len(data),-2**16/2,2**16/2])

    class FrequencyPlot(object):
        XLABEL_STR = 'Time'
        YLABEL_STR = 'Frequency (Hz)'
        LABEL_FONTSIZE = 12
        AUTOSCALE_ENABLE = True
        AUTOSCALE_AXIS = 'x'
        AUTOSCALE_TIGHT = True

        def __init__(self, plt, rate=44100, nttf=1024, noverlap=900, cmap='gray_r'):
            self.__plt = plt.add_subplot(312)
            self.__plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.__plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.__rate = rate
            self.__nttf = nttf
            self.__noverlap = noverlap
            self.__cmap = cmap

        def update(self, data):
            self.data = data

        def display(self):
            self.__plt.specgram(self.data, NFFT=self.__nttf, Fs=self.__rate, noverlap=self.__noverlap, cmap=self.__cmap)
            self.__plt.autoscale(enable=self.AUTOSCALE_ENABLE, axis=self.AUTOSCALE_AXIS, tight=self.AUTOSCALE_TIGHT)

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
            self.__plt = plt.add_subplot(313)
            self.__plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.__plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.__rate = rate

        def update(self, data):
            basicSignal = basic.SignalObj(data, self.__rate)
            self.__pitch = pitch = pYAAPT.yaapt(basicSignal)
            self.__pitchStep = pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='step')
            self.__pitchSpline = pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='spline')

        def display(self):
            self.__plt.clear()
            self.__plt.plot(self.__pitch.values, label=self.PITCH_LABEL, color=self.PITCH_COLOR)
            self.__plt.plot(self.__pitchStep.values, label=self.STEP_LABEL, color=self.STEP_COLOR)
            self.__plt.plot(self.__pitchSpline.values, label=self.SPLINE_LABEL, color=self.SPLINE_COLOR)
            self.__plt.legend(loc=self.LEGEND_LOC)
            self.__plt.grid
            self.__plt.axes.set_ylim([0,1000])
            self.__plt.autoscale(enable=self.AUTOSCALE_ENABLE, axis=self.AUTOSCALE_AXIS, tight=self.AUTOSCALE_TIGHT)

    class PdaPlots:
        TITLE_STR = 'Signal'
        TITLE_FONTSIZE = 14

        def __init__(self, win):
            self.__frame = Frame(win)
            self.__frame.pack(anchor=CENTER, fill=BOTH, expand=YES)
            self.__plt=Figure()
            self.__plt.suptitle(self.TITLE_STR, fontsize=self.TITLE_FONTSIZE)
            self.__subPlots = list()
            self.__mPlt = PitchDeterminationAlgorithm.MagnitudePlot(self.__plt)
            self.__subPlots.append(self.__mPlt)
            self.__fPlt = PitchDeterminationAlgorithm.FrequencyPlot(self.__plt)
            self.__subPlots.append(self.__fPlt)
            self.__pPlt = PitchDeterminationAlgorithm.PitchPlot(self.__plt)
            self.__subPlots.append(self.__pPlt)
            self.__canvas = FigureCanvasTkAgg(self.__plt, master=self.__frame)

        def update(self,data):
            for plt in self.__subPlots:
                plt.update(data)

        def display(self):
            for plt in self.__subPlots:
                plt.diplay()

    class CpuPlots(PdaPlots):
        def __init__(self, frame):
            super(PitchDeterminationAlgorithm.CpuPlots,self).__init__(frame)

    class GpuPlots(PdaPlots):
        def __init__(self, frame):
            super(PitchDeterminationAlgorithm.GpuPlots,self).__init__(frame)

    ### Processing Classes ###

    ## Class to handle pitch processing
    #  This is a sigleton so that only one instance keeps processed data.
    class PitchTracker(object, metaclass=Singleton):

        # Methods

        ## Constructor
        def __init__(self):
            self.__mode = PitchDeterminationAlgorithm.ProcessingModes.CPU
            self.__data = None
            self.__elapsedTime = 0.0
            self.__pitch = None
            self.__file = None

        @property
        def mode(self):
            return self.__mode
            
        @mode.setter
        def mode(self, values):
            self.__mode = values

        ## Sets the data to be processed
        #  @param values: sound samples
        def data(self, values):
            self.__data = values

        data = property(None, data)

        def file(self, values):
            self.__file = values
            self.__loadFile()
            self.__track()

        file = property(None, file)

        def track(self):
            self.__elapsedTime = process_time()
            self.__track()
            self.__elapsedTime = process_time() - self.__elapsedTime

        @property
        def elapsedTime(self):
            return self.__elapsedTime

        @property
        def pitch(self):
            return self.__pitch

        @property
        def step(self):
            return self.__step

        @property
        def spline(self):
            return self.__spline

        def __loadFile(self):
            if not os.path.isfile(self.__file):
               return
            raw = wave.open(self.__file, "r")
            if raw.getnchannels() == 2:
                return
            signal = spf.readframes(-1)
            self.__data = np.frombuffer(signal, dtype='int16')
            raw.close()

        def __track(self):
            self.__pitch = pitch
            self.__stepInterp = pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='step')
            self.__splineInterp = pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='spline')

        def __getTrackedPitch(self):
            if true:
                basicSignal = basic.SignalObj(self.__data, self.__rate)
                pitch = pYAAPT.yaapt(self.__basicSignal)
            else:
                basicSignal = basic.SignalObj(self.__data, self.__rate)
                pitch = pYAAPT.yaapt(self.__basicSignal)
            return pitch

###################################
### Designated Start of Program ###
###################################
if __name__ == '__main__':
    pda = PitchDeterminationAlgorithm()     # instantiate PDA object
    pda.run()                               # activate PDA object