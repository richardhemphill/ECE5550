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

class PitchDeterminationAlgorithm(object):

    # Inner Classes
    class Gui:
        PDA_TITLE="Pitch Determination Algorithm"   # window title
        WINDOW_PERCENT_SCREEN=0.75                  # use 75% screen width and height

        def __init__(self):
            self.window=Tk()
            self.__configureWindow(self.window)
            self.commandForm=PitchDeterminationAlgorithm.CommandForm(self.window)
            self.pdaPlots=PitchDeterminationAlgorithm.PdaPlots(self.window)

        def run(self):
            self.window.mainloop()

        def __configureWindow(self, window):
            window.geometry(self.__windowSize(window))
            window.resizable(width=True, height=True)
            window.title(self.PDA_TITLE)

        def __windowSize(self,window):
            # get screen size
            screenWidth=window.winfo_screenwidth()
            screenHeight=window.winfo_screenheight()

            # set window size to be within screen
            windowWidth=int(screenWidth*self.WINDOW_PERCENT_SCREEN)
            windowHeight=int(screenHeight*self.WINDOW_PERCENT_SCREEN)

            # format to string that for geometry call
            return "{}x{}".format(windowWidth,windowHeight)

    class CommandForm:
        def __init__(self, window):
            f=Frame(window)
            self.processorSwitch = PitchDeterminationAlgorithm.ProcessorSwitch(f)
            self.sourceSwitch = PitchDeterminationAlgorithm.SourceSwitch(f)
            self.fileBrowser = PitchDeterminationAlgorithm.FileBrowser(f)
            f.pack(anchor=N, fill=X, expand=YES)

    class CommandSwitch:
        DEFAULT_MODE=1              # default to GPU mode
        DEFAULT_COLOR='light blue'  # default color to blue

        def __init__(self, frm, modes, default=DEFAULT_MODE, color=DEFAULT_COLOR):
           f=Frame(frm)
           self.switch = IntVar(frm,self.DEFAULT_MODE)
           for (text, mode) in modes.items():
                r = Radiobutton(f, text=text, variable=self.switch,
                    value=mode, indicator=0, background=color)
                r.pack(side=LEFT)
           f.pack(side=LEFT, padx=10)

    class ProcessorSwitch(CommandSwitch):
        MODES={"GPU":1,"CPU":2}
        DEFAULT_MODE=1              # default to GPU mode
        SWITCH_COLOR='light blue'

        def __init__(self, form):
            super().__init__(form, self.MODES, self.DEFAULT_MODE, self.SWITCH_COLOR)

    class SourceSwitch(CommandSwitch):
        MODES={"MIC":1,"FILE":2}
        DEFAULT_MODE=2              # default to File mode
        SWITCH_COLOR='pink'

        def __init__(self, form):
            super().__init__(form, self.MODES, self.DEFAULT_MODE, self.SWITCH_COLOR)

    class FileBrowser:
        def __init__(self, frm):
            f=Frame(frm)
            self.srcFile=StringVar()
            self.prevSrcFile=''
            l=Entry(f, textvariable=self.srcFile, justify=LEFT)
            l.bind("<Return>", self.OnFileEntryClick)
            l.pack(side=LEFT, fill=X, expand=YES)
            b=Button(f, text="Browse", command=lambda:self.loadFile())
            b.pack(side=LEFT)
            f.pack(side=LEFT, padx=10, fill=X, expand=YES)

        def loadFile(self):
            fileName=askopenfilename(title = "Select sound file",
                filetypes = (("Wave files","*.wav"), 
                             ("MP3 files","*.mp3")))
            self.srcFile.set(fileName)
            self.srcMode.set(self.INPUT_SOURCES.get('FILE'))
            #self.processSignals()

        def OnFileEntryClick(self, event):
            value=self.srcFile.get().strip()
            changed = True if self.prevSrcFile != value else False
            if changed:
                self.srcMode.set(self.INPUT_SOURCES.get('FILE'))
                self.processSignals()
            self.prevSrcFile=value

    class MagnitudePlot:
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

    class FrequencyPlot:
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

    class PitchPlot:
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

    # PDA Constructor
    def __init__(self):
        self.gui=PitchDeterminationAlgorithm.Gui()

    # Main Run Loop
    def run(self):
        self.gui.run()

if __name__ == '__main__':
    pda = PitchDeterminationAlgorithm()
    pda.run()