#import time
#from time import process_time
#import importlib
from tkinter import *
#from tkinter import messagebox
#from tkinter.filedialog import askopenfilename
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
        def __init__(self):
            self.window=Tk()
            self.commandForm=PitchDeterminationAlgorithm.CommandForm(self.window)
            self.pdaPlots=PitchDeterminationAlgorithm.PdaPlots(self.window)

    class CommandForm:
        def __init__(self, win):
            pass

    class ProcessorSwitch:
        def __init__(self, frm):
            pass

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
            self.mPlt = PitchDeterminationAlgorithm.MagnitudePlot(self.plt)
            self.fPlt = PitchDeterminationAlgorithm.FrequencyPlot(self.plt)
            self.pPlt = PitchDeterminationAlgorithm.PitchPlot(self.plt)
            self.canvas = FigureCanvasTkAgg(self.plt, master=self.frame)

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
        print('running')

if __name__ == '__main__':
    pda = PitchDeterminationAlgorithm()
    pda.run()
