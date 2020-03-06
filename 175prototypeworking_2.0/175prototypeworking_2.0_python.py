import matplotlib.pyplot as plt
import serial 
import sounddevice as sd
import binascii
import math
import cmath
import numpy as np
import scipy
from scipy.signal import residue
from scipy import signal
import cv2
import Tkinter as tk
from tkinter import *
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#file_to_open = "C:\Users\Henry\AppData\Roaming\SPB_Data\.spyder\RECORD.raw"
contents1=str()
contents=str()
central=str()
ser = serial.Serial("COM7",9600)
i=1
x=str()
mode=str(0)
N=7
p1=str(1000);
p2=str(1000);
Filtertype='lowpass';
fftx=np.fft.rfft([str(0),str(0)])
psd=int(0)
y=[str(0),str(0)]
freqs=int(0)
h=int(0)
info=[str(0),str(1)]
print(len(info))
w, h = signal.freqz(info)
#with open(file_to_open, 'rb') as f: #take this out
#                central=f.read();
W=np.arange(-math.pi,math.pi,.01);
def Filter(N,fc,fs):
    N=float(N); #Nth order butterworth filter
    fc=float(fc); #cutoff frequency
    fs=float(fs); #sampling frequency
    wc=float(2*math.pi*fc/fs);
    T=1/fs
    omega_c=(2/T)*math.tan(wc/2);
    omega_c=2*math.pi*fc
    s_k=[omega_c*cmath.exp(cmath.sqrt(-1)*math.pi*(N+2*k-1)/(2*N)) for k in range(1, int(N)+1)];
    s_k_poly=np.poly(s_k);
    [a_k,p,s]=scipy.signal.residue(math.pow(omega_c,N),s_k_poly);
    return [sum([T*a_k[k]/(1-cmath.exp(p[k]*T)*cmath.exp(-1*cmath.sqrt(-1)*W[w])) for k in range(0,int(N))]) for w in range(0,len(W))]


def HighPass(N,fc,fs1,info):
    x=signal.butter(N, float(fc), 'high',output='sos', fs=int(fs1))
    return signal.sosfilt(x,info)


def LowPass(N,fc,fs1,info):
    x=signal.butter(N, float(fc), 'low',output='sos', fs=float(fs1), analog=False)
    return signal.sosfilt(x,info)

def BandPass(N,fc,fc2, fs1, info):    
    x=signal.butter(N,[float(fc),float(fc2)],"bandpass",fs=int(fs1),analog=False,output='sos')
    return signal.sosfilt(x,info)

def u16(value):
    return(hex(value & 0xffff)[2:6].zfill(4))
    
def s16(value):
    return-(value & 0x8000)|(value & 0x7fff)
    
def BinaryTransform( info):
    x=str()
    for j in range(0,len(info)):
        x=x+(u16(int(info[j]*32767))[2:4]+u16(int(info[j]*32767))[0:2])
    return x
        
def IntegerTransform(contents):
    x=binascii.b2a_hex(contents) #original code
    info = [float(s16(int((x[k+2:k+4]+x[k+0:k+2]),16)))/32767 for k in range(0, len(x),4)] #original code
    return info #original code
    
def serialread(x):
    contents1=str();
    while ser.in_waiting:
        contents1=contents1+ser.read()
    return contents1
def guiPF():
    global y
    sd.play(y)
    return

def guiPO():
    global info
    sd.play(info)
    return

def guiBP():
    global Filtertype
    Filtertype="bandpass"
    tk.Label(root, text = "Filter Type: " + Filtertype).grid(row=7, column=0)
    return

def guiLP():
    global Filtertype
    Filtertype="lowpass"
    tk.Label(root, text = "Filter Type: " + Filtertype).grid(row=7, column=0)
    return

def guiHP():
    global Filtertype
    Filtertype="highpass"
    tk.Label(root, text = "Filter Type: " + Filtertype).grid(row=7, column=0)
    return

def gui(info,fftx,freqs,psd,y,p1,p2,w,h,Filtertype):
    fig = plt.figure(1)
    plt.clf()
    ax1= plt.subplot(511)
    t = np.arange(0,len(info),1)
    plt.plot(t,info)
    plt.title('Original Signal')
    ax2= plt.subplot(512)
    t = np.arange(0,len(fftx),1)
    plt.plot(t,abs(fftx))
    plt.title('FFT')
    ax3= plt.subplot(513)
    ax3.plot(freqs,psd)
    plt.title('PSD')
    ax4= plt.subplot(514)
    #w, h = signal.freqz(x4)                             #done
    plt.plot(w, 20 * np.log10(abs(h)), 'b')
    plt.title('Phase Response')
    plt.ylabel('Amplitude [dB]', color='b')
    plt.xlabel('Frequency [rad/sample]')
    ax5= plt.subplot(515)
    plt.plot(y[0:len(y)])
    plt.plot('filter')
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=root)
    plot_widget = canvas.get_tk_widget()
    plot_widget.grid(row=0, column=0)
    #tk.Button(root,text="Update",command=exit).grid(row=3, column=0)
    #tk.Button(root,text="Update1",command=update1).grid(row=4, column=0)
    tk.Button(root,text="HighPass",command=guiHP).grid(row=8, column=0)
    tk.Button(root,text="LowPass",command=guiLP).grid(row=9, column=0)
    tk.Button(root,text="BandPass",command=guiBP).grid(row=10, column=0)
    tk.Button(root,text="Play Original",command=guiPO).grid(row=11, column=0)
    tk.Button(root,text="Play Filtered",command=guiPF).grid(row=12, column=0)
    tk.Label(root, text="Potentiometer1: " + p1).grid(row=5,column=0)
    tk.Label(root, text="Potentiometer2: " + p2).grid(row=6,column=0)
    tk.Label(root, text = "Filter Type: " + Filtertype).grid(row=7, column=0)
    
    
def dummy():   
    global contents
    global info
    global Filtertype
    global y
    global timeOfsample
    global N
    global p1
    global p2
    global x
    global fftx
    global psd
    global y
    global freqs
    global h
    global info
    global x
    global w
    
    while ser.in_waiting:
        mode=ser.read()
        
        if (mode=="0"): #stop recording button
            contents=serialread(x);
            info=IntegerTransform(contents);

            if(Filtertype=='lowpass'):
                y=LowPass(N,p1,44100,info);
                Na = 600
                T = 1/ 800
                x = np.linspace(0.0, Na*T, Na)
                xf = np.linspace(0.0, 1.0/(2.0/800), 600/2)
                Time = np.linspace(0, len(info) / 44100, num=len(info))
                fftx = np.fft.rfft((y))
                fftx1 = np.fft.rfft((info))
                w, h = signal.freqz(info)
                freqs,psd = signal.welch(info, 44100, nperseg=1024)  
                print("Number of total samples:")
                print(len(info))
                timeOfsample = float(len(info)) / float(44100)
                print("Time of sample:")
                print(float(timeOfsample))
                #sd.play(y)
            if(Filtertype=='highpass'):
                y=HighPass(N,p1,44100,info);
                
                Time = np.linspace(0, len(info) / 44100, num=len(info))
                fftx = np.fft.rfft((y))
                fftx1 = np.fft.rfft((info))
                w, h = signal.freqz(info)
                freqs,psd = signal.welch(info, 44100, nperseg=1024)  
                print("Number of total samples:")
                print(len(info))
                timeOfsample = float(len(info)) / float(44100)
                print("Time of sample:")
                print(float(timeOfsample))
                #sd.play(y)
            if(Filtertype=='bandpass'):
                y=BandPass(N,p1,p2,44100,info);
                Time = np.linspace(0, len(info) / 44100, num=len(info))
                fftx = np.fft.rfft((y))
                fftx1 = np.fft.rfft((info))
                w, h = signal.freqz(info)
                freqs,psd = signal.welch(info, 44100, nperseg=1024)  
                print("Number of total samples:")
                print(len(info))
                timeOfsample = float(len(info)) / float(44100)
                print("Time of sample:")
                print(float(timeOfsample))
                
            info2=BinaryTransform(y)
            gui(info,fftx,freqs,psd,y,p1,p2,w,h,Filtertype) 
            print('kk')
            ser.write(binascii.a2b_hex(info2));
            
            print('done')
        if('1'==mode):
            Filtertype='lowpass'
            tk.Label(root, text = "Filter Type: " + Filtertype).grid(row=7, column=0)
            print('lowpass')
            
        if('2'==mode):
            Filtertype='highpass'
            tk.Label(root, text = "Filter Type: " + Filtertype).grid(row=7, column=0)
            print('highpass')
            
        if('3'==mode):
            Filtertype='bandpass'
            tk.Label(root, text = "Filter Type: " + Filtertype).grid(row=7, column=0)
            print('bandpass')
            
        if ('4'==mode):
            p1=str();
            while ser.in_waiting:
                p1=p1+ser.read();
            tk.Label(root, text="Potentiometer1: " + p1).grid(row=5,column=0)
            print('p1: ')
            print(p1);
            
        if('5'==mode):
            p2=str();
            while ser.in_waiting:
                p2=p2+ser.read();
            tk.Label(root, text="Potentiometer2: " + p2).grid(row=6,column=0)
            print('p2: ')
            print(p2);
    root.after(1,dummy)
root = tk.Tk() 
gui(info,fftx,freqs,psd,y,p1,p2,w,h,Filtertype)  
dummy()
root.after(1, dummy)
root.mainloop()