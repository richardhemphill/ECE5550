import pyaudio
import numpy as np
import time
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
#import amfm_decompy.pYAAPT as pYAAPT
#import amfm_decompy.basic_tools as basic
import amfm_decompy_cuda.pYAAPT as pYAAPT
import amfm_decompy_cuda.basic_tools as basic
import wave
from pathlib import Path

RATE = 4800                     # record at samples/second
PROC_FREQ = 10                  # frequency of processing samples
CHUNK = int(RATE/PROC_FREQ)     # number of samples to process
REC_TIME = 5                    # number of seconds to record data
MIC = False                     # process with microphone.  otherwise, file
SAVE_MIC = False                # store microphone data to file
SOUND_FILE = 'soundFile.wav'    # test file with sound recording
SAVE_FILE = 'output.wav'        # output file from microphone

def magPlot(data,plt):
    plt.clear()
    plt.plot(data)
    plt.axis([0,len(data),-2**16/2,2**16/2])

def freqPlot(data,plt):
    plt.specgram(data, NFFT=1024, Fs=RATE, noverlap=900, cmap='gray_r')
    plt.autoscale(enable=True, axis='x', tight=True)

def pitchPlot(data,plt):
    plt.clear()
    basicSignal = basic.SignalObj(data,RATE)
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

if __name__=="__main__":
    w=Tk()
    w.geometry('800x600')
    w.resizable(width=True, height=True)
    w.title("Pitch Determination Algorithm")
    f=Frame(w)
    f.pack(anchor=CENTER, fill=BOTH, expand=YES)
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
    canvas = FigureCanvasTkAgg(plt, master=f)
    if(MIC):
        p=pyaudio.PyAudio()
        stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
                      frames_per_buffer=CHUNK)
        if(SAVE_MIC):
            wf=wave.open(SAVE_FILE,'wb')
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(RATE)
        for i in range(0, int((RATE/CHUNK) * REC_TIME)): #do this for 10 seconds
            data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            if(SAVE_MIC): wf.writeframes(data)
            magPlot(data,mPlt)
            freqPlot(data,fPlt)
            pitchPlot(data,pPlt)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        stream.stop_stream()
        stream.close()
        p.terminate()
        if(SAVE_MIC): wf.close()
    else:
        if Path(SOUND_FILE).exists():
            spf = wave.open(SOUND_FILE, "r")
            data = spf.readframes(-1)
            data = np.frombuffer(data, dtype='int16')
            spf.close()
            magPlot(data,mPlt)
            freqPlot(data,fPlt)
            pitchPlot(data,pPlt)
            canvas.draw()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            w.mainloop()