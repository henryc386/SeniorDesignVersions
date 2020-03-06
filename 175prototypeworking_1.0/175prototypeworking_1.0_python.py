import matplotlib.pyplot as plt
import serial 
import sounddevice as sd
import binascii
import soundfile as sf
import math
import cmath
import numpy as np
import scipy
import signal as time
from scipy.signal import residue
import cv2


#file_to_open = "C:\Users\Henry\AppData\Roaming\SPB_Data\.spyder\RECORD.raw"
contents1=str()
contents=str()
central=str()
ser = serial.Serial("COM7",9600)
i=1
x=str()
mode=str(0)
W=np.arange(-math.pi,math.pi,.1);
#with open(file_to_open, 'rb') as f: #take this out
#                central=f.read();
def Filter(N,fc):
    N=float(N); #Nth order butterworth filter
    fc=float(fc); #desired frequency
    fs=float(44100); #sampling frequency
    wc=float(2*math.pi*fc/fs);
    T=1/fs
    omega_c=(2/T)*math.tan(wc/2);
    s_k=[omega_c*cmath.exp(cmath.sqrt(-1)*math.pi*(N+2*k-1)/(2*N)) for k in range(1, int(N)+1)];
    s_k_poly=np.poly(s_k);
    [a_k,p,s]=scipy.signal.residue(math.pow(omega_c,N),s_k_poly);
    return [sum([T*a_k[k]/(1-cmath.exp(p[k]*T)*cmath.exp(-1*cmath.sqrt(-1)*W[w])) for k in range(0,int(N))]) for w in range(0,len(W))]

def HighPass(N,fc,info):
    plt.clf()
    fig = plt.figure(1)
    ax1= plt.subplot(141)
    highpass=Filter(N,fc);
    plt.plot((44100*.5/np.pi)*W,1-np.absolute(highpass)) #plots high pass filter
    return np.convolve(info,(1-np.absolute(highpass)))

def LowPass(N,fc,info):
    plt.clf()
    fig = plt.figure(1)
    ax1= plt.subplot(141)
    lowpass=Filter(N,fc);
    plt.plot((44100*.5/np.pi)*W,np.absolute(lowpass)) #plots low pass filter
    return np.convolve(info,np.absolute(lowpass))

def BandPass(N,fc,fc2, info):    
    lowpass=LowPass(N,float(fc),info);
    return HighPass(N,(fc2),lowpass);


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
    #with open(file_to_open, 'rb') as f: #take this out
     #           x = binascii.b2a_hex(f.read()) #take this out
    info = [float(s16(int((x[k+2:k+4]+x[k+0:k+2]),16)))/32767 for k in range(0, len(x),4)] #original code
    return info #original code
    
def serialread(x):
    contents1=str();
    while ser.in_waiting:
        contents1=contents1+ser.read()
        #print(contents1)
        #timeout(.1)
    #print(contents1)
    #print('z')
    #sd.play(contents1)
    return contents1
#def serialwrite(info):
#    (send data back to teensy)
    
def fft(info):
    print("yup")
    
#def Filter(Filter, info):
#    if Filter=highpass:
#        (apply highpass to info)
#    if Filter=lowpass:
#        (apply lowpass to info)
#    if Filter=bandpass:
#        (apply bandpass to info)
N=7
p1=str(1000);
p2=str();
Filtertype='lowpass';
while True:    
    while ser.in_waiting:
        mode=ser.read()
        
        if (mode=="0"): #stop recording button
            print('mode 0')
            contents=serialread(x);
#            mode='6';
#        if(mode=='6'):
            info=IntegerTransform(contents);
            #print(info)
            #sd.play(info)
            
            #sd.play(info2)
            #print(contents)
            if(Filtertype=='lowpass'):
                y=LowPass(N,p1,info);
                N = 600
                T = 1/ 800
                x = np.linspace(0.0, N*T, N)
                xf = np.linspace(0.0, 1.0/(2.0/800), 600/2)
                Time = np.linspace(0, len(info) / 44100, num=len(info))
                fftx = np.fft.rfft((y))
                fftx1 = np.fft.rfft((info))
                ax2 = plt.subplot(142)
                ax2.plot(abs(fftx))
                #ax2.plot(y)
                ax3 = plt.subplot(143)
                ax3.plot(fftx1)
                print(sum(abs(fftx1)))
                ax4 = plt.subplot(144)
                ax4.plot(abs(fftx))
        
                
                #ax3.plot(info)
                ax2.title.set_text('lpf+signal')
                ax3.title.set_text('info')
                ax4.title.set_text('Original Signal')
                print("Number of total samples:")
                print(len(info))
                timeOfsample = float(len(info)) / float(44100)
                print("Time of sample:")
                print(float(timeOfsample))
                #sd.play(y)
            if(Filtertype=='highpass'):
                y=HighPass(N,p1,info);
                
                Time = np.linspace(0, len(info) / 44100, num=len(info))
                fftx = np.fft.rfft((y))
                fftx1 = np.fft.rfft((info))
                ax2 = plt.subplot(142)
                ax2.plot(abs(fftx))
                #ax2.plot(y)
                ax3 = plt.subplot(143)
                ax3.plot(abs(fftx1))
                ax4 = plt.subplot(144)
                ax4.plot(Time,info)
                
                #ax3.plot(info)
                ax2.title.set_text('hpf+signal')
                ax3.title.set_text('info')
                ax4.title.set_text('Original Signal')
                print("Number of total samples:")
                print(len(info))
                timeOfsample = float(len(info)) / float(44100)
                print("Time of sample:")
                print(float(timeOfsample))
                #sd.play(y)
            if(Filtertype=='bandpass'):
                y=BandPass(N,p1,p2,info);
                
            y = y/max(y)
            abs(y)
            sd.play(y)
            
            info2=BinaryTransform(y)
            #o=IntegerTransform(binascii.a2b_hex(info2))
            #sd.play(o)
            #ser.write("w");
            
            print('kk')
            
            #ser.write(central);
            #i=0;
            #while(i<4):
            ser.write(binascii.a2b_hex(info2));
            #i=i+1;
            print('done')
            #with open(file_to_open, 'rb') as f: #take this out
            #    central=f.read();
            #for j in range(0, len(central)):
            #    ser.write(central[j]);
                #print(f.read());
            #info=IntegerTransform(contents)
            #print(x)
            #ser.write(x[0])
            #sd.play(info)
            #print('2')
            #r=ser.read();
            #print(x)
            #print('1')
#            y=BinaryTransform(x,info)
            #print(x)
            #serialwrite(info);
#        if (mode=='1'): #start playing button
#            fft(info);
#            i=0
        if('1'==mode):
            Filtertype='lowpass'
            print('lowpass');
        if('2'==mode):
            Filtertype='highpass'
            print('highpass')
        if('3'==mode):
            Filtertype='bandpass'
            print('bandpass')
            #print(p2);
            
        if ('4'==mode):
            p1=str();
            while ser.in_waiting:
                p1=p1+ser.read();
            print('p1: ')
            print(p1);
            
        if('5'==mode):
            p2=str();
            while ser.in_waiting:
                p2=p2+ser.read();
            print('p2: ')
            print(p2);
            
            

sd.play(info)
plt.plot(info)  
sd.play(info)