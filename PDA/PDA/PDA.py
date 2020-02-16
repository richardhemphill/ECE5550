import amfm_decompy.pYAAPT as pYAAPT
import amfm_decompy.basic_tools as basic
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib as mpl
import wave
import sys


spf = wave.open("f1nw0000pes_short.wav", "r")
# Extract Raw Audio from Wav File
signal = spf.readframes(-1)
signal = np.frombuffer(signal, dtype='int16')


# If Stereo
if spf.getnchannels() == 2:
    print("Just mono files")
    sys.exit(0)

plt.figure(1)
a = plt.subplot(311)    
plt.title("Signal", fontsize=14)
a.set_xlabel("Samples", fontsize=12)
a.set_ylabel("Magnitude", fontsize=12)
plt.plot(signal)
plt.autoscale(enable=True, axis='x', tight=True)

b    = plt.subplot(312)
axes = plt.gca()
Pxx, freqs, bins, im = b.specgram(signal, NFFT=1024, Fs=16000, noverlap=900, cmap='gray_r') 
b.set_xlabel('Time', fontsize=12)    
b.set_ylabel('Frequency [Hz]', fontsize=12) 
plt.autoscale(enable=True, axis='x', tight=True)
#axes.set_ylim([ymin,ymax])
#plt.show()

signal = basic.SignalObj('f1nw0000pes_short.wav')

pitch  = pYAAPT.yaapt(signal, frame_length=40, tda_frame_length=40, f0_min=75, f0_max=600)
c = plt.subplot(313)
plt.plot(pitch.values, label='pich interpolation', color='green')
pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='step')
plt.plot(pitch.values, label='step interpolation', color='blue')
pitch.set_values(pitch.samp_values, len(pitch.values), interp_tech='spline')
plt.plot(pitch.values, label='spline interpolation', color='red')
plt.grid
c.set_xlabel('Samples', fontsize=12)
c.set_ylabel('Pitch (Hz)', fontsize=12)
c.legend(loc='upper right')
plt.autoscale(enable=True, axis='x', tight=True)
axes = plt.gca()
axes.set_ylim([0,1000])

plt.show()