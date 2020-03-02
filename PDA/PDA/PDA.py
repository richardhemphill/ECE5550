import time
from time import process_time
import importlib
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import amfm_decompy.pYAAPT as pYAAPT
import amfm_decompy.basic_tools as basic
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as pplt 
import numpy as np
import wave
import sys
import os
import pyaudio

class PDA(object):

    # Constants
    PDA_TITLE="Pitch Determination Algorithm"   # window title
    WINDOW_GEOMETRY='640x480'                   # default size
    WINDOW_PERCENT_SCREEN=0.75                  # use 75% screen width and height
    PROCESSING_MODES={"GPU":1,"CPU":2}
    INPUT_SOURCES={"MIC":1,"FILE":2}
    DEFAULT_SOURCE_FILE="Source Sound File"
    RATE = 44100
    CHUNK = int(RATE/20) # RATE / number of updates per second

    # Member Variables


    # Inner Classes
    class PdaInner:
        def __str__(self):
            return type(self).__name__

    class MagnitudePlot(PdaInner):
        XLABEL_STR = 'Samples'
        YLABEL_STR = 'Magnitude'
        LABEL_FONTSIZE = 12

        def __init__(self, plt):
            self.plt = plt.add_subplot(311)
            self.plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)

        def update(self, data):
            self.plt.clear()
            self.plt.plot(data)
            self.plt.axis([0,len(data),-2**16/2,2**16/2])

    class FrequencyPlot(PdaInner):
        XLABEL_STR = 'Time'
        YLABEL_STR = 'Frequency (Hz)'
        LABEL_FONTSIZE = 12
        AUTOSCALE_ENABLE = True
        AUTOSCALE_AXIS = 'x'
        AUTOSCALE_TIGHT = TRUE

        def __init__(self, plt, rate=44100, nttf=1024, noverlap=900, cmap='gray_r'):
            self.plt = plt.add_subplot(312)
            self.plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.rate = rate
            self.nttf = nttf
            self.noverlap = noverlap
            self.cmap = cmap

        def update(self, data):
            self.plt.specgram(data, NFFT=self.nttf, Fs=self.rate, noverlap=self.noverlap, cmap=self.cmap)
            self.plt.autoscale(enable=self.AUTOSCALE_ENABLE, axis=self.AUTOSCALE_AXIS, tight=self.AUTOSCALE_TIGHT)

    class PitchPlot(PdaInner):
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
        AUTOSCALE_TIGHT = TRUE

        def __init__(self, plt, rate=44100):
            self.plt = plt.add_subplot(313)
            self.plt.set_xlabel(self.XLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.plt.set_ylabel(self.YLABEL_STR, fontsize=self.LABEL_FONTSIZE)
            self.rate = rate

        def update(self, data):
            self.plt.clear()
            basicSignal = basic.SignalObj(data, self.rate)
            pitch = pYAAPT.yaapt(basicSignal)
            self.plt.plot(pitch.values, label=self.PITCH_LABEL, color=self.PITCH_COLOR)
            pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='step')
            self.plt.plot(pitch.values, label=self.STEP_LABEL, color=self.STEP_COLOR)
            pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='spline')
            self.plt.plot(pitch.values, label=self.SPLINE_LABEL, color=self.SPLINE_COLOR)
            self.plt.legend(loc=self.LEGEND_LOC)
            self.plt.grid
            self.plt.axes.set_ylim([0,1000])
            self.plt.autoscale(enable=self.AUTOSCALE_ENABLE, axis=self.AUTOSCALE_AXIS, tight=self.AUTOSCALE_TIGHT)

    class PdaPlots(PdaInner):
        TITLE_STR = 'Signal'
        TITLE_FONTSIZE = 14

        def __init__(self, frame):
            self.frame = frame
            self.frame.pack(anchor=CENTER, fill=BOTH, expand=YES)
            self.plt=Figure()
            self.plt.suptitle(self.TITLE_STR, fontsize=self.TITLE_FONTSIZE)
            self.mPlt = PDA.MagnitudePlot(self.plt)
            self.fPlt = PDA.FrequencyPlot(self.plt)
            self.pPlt = PDA.PitchPlot(self.plt)
            self.canvas = FigureCanvasTkAgg(self.plt, master=self.frame)

    class CpuPlots(PdaPlots):
        def __init__(self, frame):
            super(PDA.CpuPlots,self).__init__(frame)

    class GpuPlots(PdaPlots):
        def __init__(self, frame):
            super(PDA.GpuPlots,self).__init__(frame)

    # PDA Constructor
    def __init__(self):
        self.display()

    # Main Run Loop
    def run(self):
        print("Done")

    # Utilities
    # Sets window size
    def windowSize(self,containerWindow):
        # get screen size
        screenWidth=containerWindow.winfo_screenwidth()
        screenHeight=containerWindow.winfo_screenheight()

        # set window size to be within screen
        windowWidth=int(screenWidth*self.WINDOW_PERCENT_SCREEN)
        windowHeight=int(screenHeight*self.WINDOW_PERCENT_SCREEN)

        # format to string that for geometry call
        return "{}x{}".format(windowWidth,windowHeight)

    # Contructs User GUI
    def display(self):
        w=Tk()
        self.window=w
        self.configureWindow(w)
        self.configureCmdFrm(w)
        self.configurePlotFrm(w)
        self.configureTimerFrm(w)
        w.mainloop()

    # Window
    def configureWindow(self, containerWindow):
        containerWindow.geometry(self.windowSize(containerWindow))
        containerWindow.resizable(width=True, height=True)
        containerWindow.title(self.PDA_TITLE)

    # Window Frames

    ## Control Frame
    def configureCmdFrm(self,containerWindow):
        f=Frame(containerWindow)
        self.gpuSwitch(f)
        self.srcSwitch(f)
        self.fileBrowser(f)
        f.pack(anchor=N, fill=X, expand=YES)

    def gpuSwitch(self, containerFrame):
        f=Frame(containerFrame)
        self.procMode = IntVar(containerFrame,1) # default to GPU mode
        for (text, mode) in self.PROCESSING_MODES.items():
            r = Radiobutton(f, text=text, variable=self.procMode,
                value=mode, indicator=0, background="light blue")
            r.pack(side=LEFT)
        f.pack(side=LEFT, padx=10)

    def srcSwitch(self, containerFrame):
        f=Frame(containerFrame)
        self.srcMode = IntVar(containerFrame,1) # default to MIC mode
        for (text, mode) in self.INPUT_SOURCES.items():
            r = Radiobutton(f, text=text, variable=self.srcMode, 
                value=mode, indicator=0, background="pink",
                command=lambda: self.processSignals())
            r.pack(side=LEFT)
        f.pack(side=LEFT, padx=10)

    ## Plot Frame
    def configurePlotFrm(self, containerWindow):
        f=Frame(self.window)
        f.pack(anchor=CENTER, fill=BOTH, expand=YES)
        self.plotFrame=f

    ## Processing Timer Frame
    def configureTimerFrm(self, containerWindow):
        f=Frame(containerWindow)
        lUnit=Label(f,text='seconds')
        lUnit.pack(side=RIGHT)
        self.processingTime=StringVar()
        self.processingTime.set('TBD')
        lValue=Label(f,textvariable=self.processingTime)
        lValue.pack(side=RIGHT)
        f.pack(anchor=SE, fill=X, expand=YES)

    # Process Signals
    def processSignals(self):
        if self.srcMode.get() == self.INPUT_SOURCES.get('MIC'):
            self.procesSignalsFromMic()
        else:
            self.procesSignalsFromFile()

    def magPlot(self,data,plt):
        plt.clear()
        plt.plot(data)
        plt.axis([0,len(data),-2**16/2,2**16/2])

    def freqPlot(self,data,plt):
        plt.specgram(data, NFFT=1024, Fs=44100, noverlap=900, cmap='gray_r')
        plt.autoscale(enable=True, axis='x', tight=True)

    def pitchPlot(self,data,plt,rate):
        plt.clear()
        basicSignal = basic.SignalObj(data,rate)
        pitch  = pYAAPT.yaapt(basicSignal)
        plt.plot(pitch.values, label='pich interpolation', color='green')
        pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='step')
        plt.plot(pitch.values, label='step interpolation', color='blue')
        pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='spline')
        plt.plot(pitch.values, label='spline interpolation', color='red')
        plt.legend(loc='upper right')
        plt.grid
        plt.axes.set_ylim([0,1000])
        plt.autoscale(enable=True, axis='x', tight=True)

    def procesSignalsFromMic(self):
        RATE = 44100
        CHUNK = int(RATE/2) # RATE / number of updates per second
        plt=Figure()
        plt.suptitle("Signal", fontsize=14)
        mPlt=plt.add_subplot(311)
        mPlt.set_xlabel("Samples", fontsize=12)
        mPlt.set_ylabel("Magnitude", fontsize=12)
        fPlt=plt.add_subplot(312)
        fPlt.set_xlabel('Time', fontsize=12)    
        fPlt.set_ylabel('Frequency [Hz]', fontsize=12) 
        pPlt=plt.add_subplot(313)
        pPlt.set_xlabel('Samples', fontsize=12)
        pPlt.set_ylabel('Pitch (Hz)', fontsize=12)
        pPlt.axes = plt.gca()
        canvas = FigureCanvasTkAgg(plt, master=self.plotFrame)
        p=pyaudio.PyAudio()
        stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                      frames_per_buffer=CHUNK)
        for i in range(int(20*RATE/CHUNK)): #do this for 10 seconds
            startTime=process_time()
            data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            self.magPlot(data,mPlt)
            self.freqPlot(data,fPlt)
            self.pitchPlot(data,pPlt,RATE)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            elapsedTime=process_time()-startTime
            self.processingTime.set(elapsedTime)
        stream.stop_stream()
        stream.close()
        p.terminate()

    def procesSignalsFromFile(self):
        startTime=process_time()

        soundFile=self.srcFile.get()
        if not os.path.isfile(soundFile):
           return

        spf = wave.open(soundFile, "r")
        signal = spf.readframes(-1)
        signal = np.frombuffer(signal, dtype='int16')
        spf.close()
        if spf.getnchannels() == 2:
            return

        plt=Figure()
        plt.suptitle("Signal", fontsize=14)
        magPlt=plt.add_subplot(311)
        magPlt.set_xlabel("Samples", fontsize=12)
        magPlt.set_ylabel("Magnitude", fontsize=12)
        magPlt.plot(signal)
        magPlt.autoscale(enable=True, axis='x', tight=True)

        freqPlt=plt.add_subplot(312)
        freqPlt.set_xlabel('Time', fontsize=12)    
        freqPlt.set_ylabel('Frequency [Hz]', fontsize=12) 
        axes = plt.gca()
        freqPlt.specgram(signal, NFFT=1024, Fs=16000, noverlap=900, cmap='gray_r')
        freqPlt.autoscale(enable=True, axis='x', tight=True)

        pitchPlt=plt.add_subplot(313)
        pitchPlt.set_xlabel('Samples', fontsize=12)
        pitchPlt.set_ylabel('Pitch (Hz)', fontsize=12)
        basicSignal = basic.SignalObj(soundFile)
        pitch  = pYAAPT.yaapt(basicSignal, frame_length=40, tda_frame_length=40, f0_min=75, f0_max=600)
        pitchPlt.plot(pitch.values, label='pich interpolation', color='green')
        pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='step')
        pitchPlt.plot(pitch.values, label='step interpolation', color='blue')
        pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='spline')
        pitchPlt.plot(pitch.values, label='spline interpolation', color='red')
        pitchPlt.legend(loc='upper right')
        pitchPlt.grid
        pitchPlt.axes = plt.gca()
        pitchPlt.axes.set_ylim([0,1000])
        pitchPlt.autoscale(enable=True, axis='x', tight=True)

        canvas = FigureCanvasTkAgg(plt, master=self.plotFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        elapsedTime=process_time()-startTime
        self.processingTime.set(elapsedTime)

    # Callbacks
    def loadFile(self):
        fileName=askopenfilename(title = "Select sound file",
            filetypes = (("Wave files","*.wav"), 
                         ("MP3 files","*.mp3")))
        self.srcFile.set(fileName)
        self.srcMode.set(self.INPUT_SOURCES.get('FILE'))
        self.processSignals()

    def OnFileEntryClick(self, event):
        value=self.srcFile.get().strip()
        changed = True if self.prevSrcFile != value else False
        if changed:
            self.srcMode.set(self.INPUT_SOURCES.get('FILE'))
            self.processSignals()
        self.prevSrcFile=value

    def fileBrowser(self, containerFrame):
        f=Frame(containerFrame)
        self.srcFile=StringVar()
        self.prevSrcFile=''
        l=Entry(f, textvariable=self.srcFile, justify=LEFT)
        l.bind("<Return>", self.OnFileEntryClick)
        l.pack(side=LEFT, fill=X, expand=YES)
        b=Button(f, text="Browse", command=lambda:self.loadFile())
        b.pack(side=LEFT)
        f.pack(side=LEFT, padx=10, fill=X, expand=YES)

if __name__ == '__main__':
    PDA().run()
