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
import tkinter as tk
#from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import amfm_decompy.pYAAPT as pYAAPT
import amfm_decompy.basic_tools as basic
import amfm_decompy_cuda.pYAAPT as pYAAPT_cuda
import amfm_decompy_cuda.basic_tools as basic_cuda
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
#import matplotlib.pyplot as pplt 
import numpy as np
import cupy as cp
import wave
#import sys
import os
#import pyaudio
from enum import Enum

# Types

class Singleton(type):
    __instance=None
    def __init__(cls,name,bases,dic):
        super(Singleton,cls).__init__(name,bases,dic)
    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.__instance=super(Singleton,cls).__call__(*args,**kw)
        return cls.__instance
    @property
    def instance(cls):
        return cls.__instance

## Class containing functionality needed for Pitch Determination Algorithm
class PDA(object):

    class ProcessingModes(Enum):
        CPU  = 1
        GPU  = 2

    class InputSources(Enum):
        FILE = 1
        MIC  = 2

    ## Constructor
    def __init__(self):
        self.__gui=PDA.GUI()

    ## Starts the Pitch Determination Algorithm
    def run(self):
        self.__gui.run()


    ### PDA.GUI ###

    ## Class that sets up and manages the graphical interface.
    class GUI(object):
        # Constants
        TITLE='Pitch Determination Algorithm'   # window title
        SCREEN_PERCENT=0.5                      # percent of screen height/width

        ## Constructor
        def __init__(self):
            self.__window=tk.Tk()
            self.__configure()
            self.__command=PDA.CommandForm(self.__window)
            self.__plots=PDA.PdaPlots(self.__window)
            self.__elapsed=PDA.ElapsedTime(self.__window)
            self.__command.plots(self.__plots)


        ## Activates the GUI
        def run(self):
            self.__window.mainloop()

        ## Initializes the look of the GUI
        def __configure(self):
            self.__window.geometry(self.__size())
            self.__window.resizable(width=True, height=True)
            self.__window.title(self.TITLE)

        ## Return geometry per the size the GUI window
        def __size(self):
            # get screen size
            screenWidth=self.__window.winfo_screenwidth()
            screenHeight=self.__window.winfo_screenheight()

            # set window size to be within screen
            windowWidth=int(screenWidth*self.SCREEN_PERCENT)
            windowHeight=int(screenHeight*self.SCREEN_PERCENT)

            # format to string that for geometry call
            return "{}x{}".format(windowWidth,windowHeight)


    ### PDA.CommandForm ###

    ## Class that manages the window form for controlling the GUI.
    class CommandForm(object):

        ## Constructor
        def __init__(self, window):
            self.__frame=tk.Frame(window)
            self.__processorSwitch = PDA.ProcessorSwitch(self.__frame)
            self.__sourceSwitch = PDA.SourceSwitch(self.__frame)
            self.__fileBrowser = PDA.FileBrowser(self.__frame)
            self.__frame.pack(anchor=tk.N, fill=tk.X, expand=tk.YES)

        def plots(self,instance):
            self.__fileBrowser.plots(instance)

    ### PDA.CommandSwitch ###

    ## Genralized class for toggle switched in the GUI.
    class CommandSwitch(object, metaclass=Singleton):

        # Constants
        DEFAULT_COLOR='gray'
        DEFAULT_MODE=1

        ## Constructor
        def __init__(self, form, modes, color=None, default=DEFAULT_MODE):
            self.__frame=tk.Frame(form)
            self.__mode = tk.IntVar(form, default)
            for mode in modes:                          # itterate thru modes
                r = tk.Radiobutton(master=self.__frame) # parent widget
                r.config(text=mode.name)                # button display text
                r.config(variable=self.__mode)          # switch variable
                r.config(value=mode.value)              # value of switch
                r.config(indicatoron=False)             # raised/sunken button
                r.config(background=color)              # set color
                r.pack(side=tk.LEFT)                    # next left in parent
            self.__frame.pack(side=tk.LEFT, padx=10)

        @property
        def mode(self):
            return self.__mode

        @mode.setter
        def mode(self, value):
            self.__mode.set(value)


    ### PDA.ProcessorSwitch ###

    ## Class for toggling between which type of process will handle calculations.
    #  Parent class for switches used in GUI
    class ProcessorSwitch(CommandSwitch):
        COLOR='cornflower blue'

        ## Constructor
        def __init__(self, form):
            self.__modes=PDA.ProcessingModes
            super().__init__(form=form, modes=self.__modes, color=self.COLOR)


    ### PDA.SourceSwitch ###

    ## Class for toggling between source for auditory data.
    class SourceSwitch(CommandSwitch):
        COLOR='indian red'

        ## Constructor
        def __init__(self, form):
            self.__modes=PDA.InputSources
            super().__init__(form=form, modes=self.__modes, color=self.COLOR)


    ### PDA.FileBrowser ###

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
            self.__frame=tk.Frame(form)
            self.__sourceSwitch=PDA.SourceSwitch()
            self.__pitchTracker=PDA.PitchTracker()
            self.__plots=None
            self.__file=None
            self.__entryFile=tk.StringVar()
            self.__entry=tk.Entry(self.__frame, textvariable=self.__entryFile, justify=tk.LEFT)
            self.__entry.bind("<Return>", self.__OnFileEntryClick)
            self.__entry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
            self.__button=tk.Button(self.__frame, text=self.BUTTON_TEXT, command=lambda:self.__loadFile())
            self.__button.pack(side=tk.LEFT)
            self.__frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=tk.YES)

        def plots(self,instance):
            self.__plots=instance

        ## Open dialog window for finding/select file.
        def __loadFile(self):
            value=askopenfilename(title = self.OPEN_TITLE, filetypes = self.FILE_TYPES)
            self.__processFile(value)

        ## Action when files has been selected.
        def __OnFileEntryClick(self, event):
            value=self.__srcFile.get().strip()
            if self.__file != value:
                self.__entryFile.set(value)
                self.__processFile(value)

        def __processFile(self, value):
            self.__file=value
            self.__pitchTracker.file = self.__file
            self.__sourceSwitch.mode = PDA.InputSources.FILE
            self.__updatePlots()

        def __updatePlots(self):
            if self.__plots is None:
                tk.messagebox.showerror('Error','No Form for Plots was loaded')
            else:
                self.__plots.update()


    ### PDA.MagnitudePlot ###

    class MagnitudePlot(object):
        XLABEL_STR = 'Samples'
        YLABEL_STR = 'Magnitude'
        LABEL_FONTSIZE = 12

        def __init__(self, plt, pos):
            self.__plt = plt.add_subplot(pos)
            self.__plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.__plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.__pitchTracker=PDA.PitchTracker()

        def update(self):
            self.__plt.clear()
            data=self.__pitchTracker.data
            self.__plt.plot(data)
            self.__plt.axis([0,len(data),-2**16/2,2**16/2])


    ### PDA.FrequencyPlot ###

    class FrequencyPlot(object):
        XLABEL_STR = 'Time'
        YLABEL_STR = 'Frequency (Hz)'
        LABEL_FONTSIZE = 12
        AUTOSCALE_ENABLE = True
        AUTOSCALE_AXIS = 'x'
        AUTOSCALE_TIGHT = True

        def __init__(self, plt, pos, rate=44100, nttf=1024, noverlap=900, cmap='gray_r'):
            self.__plt = plt.add_subplot(pos)
            self.__plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.__plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.__rate = rate
            self.__nttf = nttf
            self.__noverlap = noverlap
            self.__cmap = cmap
            self.__pitchTracker=PDA.PitchTracker()

        def update(self):
            self.__plt.specgram(self.__pitchTracker.data, NFFT=self.__nttf, Fs=self.__rate, noverlap=self.__noverlap, cmap=self.__cmap)
            self.__plt.autoscale(enable=self.AUTOSCALE_ENABLE, axis=self.AUTOSCALE_AXIS, tight=self.AUTOSCALE_TIGHT)


    ### PDA.PitchPlot ###

    class PitchPlot(object):
        XLABEL = 'Samples'
        YLABEL = 'Pitch (Hz)'
        FONTSIZE = 12
        PITCH_LABEL = 'pitch interpolation'
        PITCH_COLOR = 'green'
        STEP_LABEL = 'step interpolation'
        STEP_COLOR = 'blue'
        SPLINE_LABEL = 'spline interpolation'
        SPLINE_COLOR = 'red'
        LEGEND_LOC = 'upper right'
        ENABLE = True
        AXIS = 'x'
        TIGHT = True

        def __init__(self, plt, pos):
            self.__plt = plt.add_subplot(pos)
            self.__plt.set_xlabel(xlabel=self.XLABEL, fontsize=self.FONTSIZE)
            self.__plt.set_ylabel(ylabel=self.YLABEL, fontsize=self.FONTSIZE)
            self.__pitchTracker=PDA.PitchTracker()

        def update(self):
            self.__plt.clear()
            self.__plot()
            self.__plt.legend(loc=self.LEGEND_LOC)
            self.__plt.grid
            self.__plt.axes.set_ylim([0,1000])
            self.__plt.autoscale(enable=self.ENABLE, axis=self.AXIS, tight=self.TIGHT)

        def __plot(self):
            self.__plt.plot(self.__pitchTracker.pitch, label=self.PITCH_LABEL, color=self.PITCH_COLOR)
            self.__plt.plot(self.__pitchTracker.step, label=self.STEP_LABEL, color=self.STEP_COLOR)
            self.__plt.plot(self.__pitchTracker.spline, label=self.SPLINE_LABEL, color=self.SPLINE_COLOR)

    ### PDA.PdaPlots ###

    class PdaPlots(object, metaclass=Singleton):
        TITLE_STR = 'Signal'
        TITLE_FONTSIZE = 14
        NUM_PLOTS = 3
        HORIZ = True
        PLOT_NUM = 0

        def __init__(self, win):
            self.__frame=tk.Frame(win)
            self.__frame.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=tk.YES)
            self.__plt=Figure()
            self.__plt.suptitle(self.TITLE_STR, fontsize=self.TITLE_FONTSIZE)
            self.__subPlots = list()
            self.__subPlots.append(PDA.MagnitudePlot(self.__plt,self.__pos))
            self.__subPlots.append(PDA.FrequencyPlot(self.__plt,self.__pos))
            self.__subPlots.append(PDA.PitchPlot(self.__plt,self.__pos))
            self.__canvas = FigureCanvasTkAgg(self.__plt, master=self.__frame)

        def update(self):
            for plt in self.__subPlots:
                plt.update()
            self.__canvas.draw()
            self.__canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        @property
        def __pos(self):
            self.PLOT_NUM = self.PLOT_NUM + 1
            if self.HORIZ:
                pos = '{}{}{}'.format(self.NUM_PLOTS,1,self.PLOT_NUM)
            else:
                pos = '{}{}{}'.format(self.NUM_PLOTS,self.PLOT_NUM,1)
            return int(pos)

    ### PDA.ElapsedTime ###

    class ElapsedTime(object):
        UNIT='seconds'
        DEFAULT='TBD'

        def __init__(self, win):
            self.__frame=tk.Frame(win)
            self.__lUnit=tk.Label(self.__frame,text=self.UNIT)
            self.__lUnit.pack(side=tk.RIGHT)
            self.__time=tk.StringVar()
            self.__time.set(self.DEFAULT)
            self.__lValue=tk.Label(self.__frame, textvariable=self.__time)
            self.__lValue.pack(side=tk.RIGHT)
            self.__frame.pack(anchor=tk.SE, fill=tk.X, expand=tk.YES)

        def time(self, value):
            self.__time.set(value)

        time = property(None, time)

    ### PDA.PitchTracker ###

    ## Class to handle pitch processing
    #  This is a sigleton so that only one instance keeps processed data.
    class PitchTracker(object, metaclass=Singleton):
        
        # Constants

        RATE=4800

        # Methods

        ## Constructor
        def __init__(self):
            self.__mode = PDA.ProcessingModes.CPU
            self.__file = None
            self.__data = None
            self.__elapsedTime = 0.0
            self.__pitch = None
            self.__step = None
            self.__spline = None

        @property
        def mode(self):
            return self.__mode
            
        @mode.setter
        def mode(self, values):
            self.__mode = values

        @property
        def data(self):
            return self.__data

        ## Sets the data to be processed
        #  @param values: sound samples
        @data.setter
        def data(self, values):
            self.__data = values

        def file(self, file):
            self.__file = file
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
            signal = raw.readframes(-1)
            self.__setData(signal)
            raw.close()

        def __setData(self, signal):
            if self.__mode == PDA.ProcessingModes.CPU:
                self.__data = np.frombuffer(signal, dtype='int16')
            else:
                self.__data = cp.frombuffer(signal, dtype='int16')

        def __track(self):
            if self.__mode == PDA.ProcessingModes.CPU:
                basicSignal = basic.SignalObj(self.__data, self.RATE)
                pitch = pYAAPT.yaapt(basicSignal)
            else:
                basicSignal = basic_cuda.SignalObj(self.__data, self.RATE)
                pitch = pYAAPT_cuda.yaapt(basicSignal)
            self.__pitch = pitch.values
            pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='step')
            self.__step = pitch.values
            pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='spline')
            self.__spline = pitch.values

###################################
### Designated Start of Program ###
###################################
if __name__ == '__main__':
    pda = PDA()     # instantiate PDA object
    pda.run()                               # activate PDA object