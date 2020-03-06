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
SCALE1A=0
SCALE2A=len(info)
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
    text7= Label(root, text = "Filter Type: " + Filtertype)
    text7.place(x=170, y=170,height=30, width=150)
    return

def guiLP():
    global Filtertype
    Filtertype="lowpass"
    text7= Label(root, text = "Filter Type: " + Filtertype)
    text7.place(x=170, y=170,height=30, width=150)
    return

def guiHP():
    global Filtertype
    Filtertype="highpass"
    text7= Label(root, text = "Filter Type: " + Filtertype)
    text7.place(x=170, y=170,height=30, width=150)
    return

def guiP1():
    global p1
    text4 = Label(text=str(float(p1)))
    text4.place(x=170, y=50,height=30, width=150)
    return

def guiP2():
    global p2
    text6 = Label(text=str(float(p2)))
    text6.place(x=170, y=130,height=30, width=150)
    return
  
def plotInfo():
    global info
    global SCALE1A
    global SCALE2A
    fig = plt.figure(1)
    plt.clf()
    #t = np.arange(0,len(info),1)
    plt.plot(info[int(SCALE1A):int(SCALE2A)])
    plt.title('Original Signal')
    canvas = FigureCanvasTkAgg(fig, master=root)
    plot_widget = canvas.get_tk_widget()
    plot_widget.place(x=390,y=10,width= 1100,height = 190)
    return

def plotFiltered():
    global y
    global SCALE1A
    global SCALE2A
    fig1 = plt.figure(2)
    plt.clf()
    #t = np.arange(0,len(info),1)
    plt.plot(y[int(SCALE1A):int(SCALE2A)])
    plt.title('Filtered Signal')
    canvas1 = FigureCanvasTkAgg(fig1, master=root)
    plot_widget1 = canvas1.get_tk_widget()
    plot_widget1.place(x=390,y=210,width= 1100,height = 190)
    return
    
def plotFFTInfo():
    global info 
    global SCALE1A
    global SCALE2A
    global fftx
    fftx = np.fft.rfft((info))    
    fig2 = plt.figure(3)
    plt.clf()
    #t = np.arange(0,len(fftx),1)
    plt.plot(fftx[int(SCALE1A):int(SCALE2A)])
    plt.title('Fast Fourier Transform Original')
    canvas2 = FigureCanvasTkAgg(fig2, master=root)
    plot_widget2 = canvas2.get_tk_widget()
    plot_widget2.place(x=390,y=410,width= 1100,height = 190)

    return

def plotFFTFiltered():
    global y
    global SCALE1A
    global SCALE2A
    fftx = np.fft.rfft((y))
    fig3 = plt.figure(4)
    plt.clf()
    #t = np.arange(0,len(fftx),1)
    plt.plot(fftx[int(SCALE1A):int(SCALE2A)])
    plt.title('Fast Fourier Transform Filtered')
    canvas3 = FigureCanvasTkAgg(fig3, master=root)
    plot_widget3 = canvas3.get_tk_widget()
    plot_widget3.place(x=390,y=610,width= 1100,height = 190)
    
    return

def plotOther2():
    global info
    global SCALE1A
    global SCALE2A
    fig4 = plt.figure(5)
    plt.clf()
    #t = np.arange(0,len(info),1)
    plt.plot(info[int(SCALE1A):int(SCALE2A)])
    plt.title('original')
    canvas4 = FigureCanvasTkAgg(fig4, master=root)    
    plot_widget4 = canvas4.get_tk_widget()   
    plot_widget4.place(x=390,y=810,width= 1100,height = 190)

    return    
        
def guiSP1():
    global P1
    P1=POT1.get()
    text4 = Label(text=P1)
    text4.place(x=170, y=50,height=30, width=150)
    return
def guiSP2():
    global P1
    P2=POT2.get()
    print(str(P2))
    text6 = Label(text=P2)
    text6.place(x=170, y=130,height=30, width=150)
    return 

def guiUOR():
    global SCALE1A
    global SCALE2A
    SCALE1A=SCALE1.get()
    SCALE2A=SCALE2.get()
    plotInfo()
    return

def guiUFI():
    global SCALE1A
    global SCALE2A
    SCALE1A=SCALE1.get()
    SCALE2A=SCALE2.get()
    plotFiltered()
    return
def guiUFFT():
    global SCALE1A
    global SCALE2A
    SCALE1A=SCALE1.get()
    SCALE2A=SCALE2.get()
    plotFFTInfo()
    return
def guiUPSD():
    global SCALE1A
    global SCALE2A
    SCALE1A=SCALE1.get()
    SCALE2A=SCALE2.get()
    plotFFTFiltered()
    return
def guiUPH():
    global SCALE1A
    global SCALE2A
    SCALE1A=SCALE1.get()
    SCALE2A=SCALE2.get()
    plotOther2()
    return

def guiTIME():
    global info
    text11=Label(text="Play Time:\n"+str(float(len(info))/float(44100))+" seconds")
    print(float(len(info)/44100))
    text11.place(x=170, y=210, height=30, width=150)
    return

def guiReceiving():
    text12=Label(text="Receiving Data\n Please Wait . . .")
    text12.place(x=170,y=250, height=30, width=150)
    return

def guiSending():
    text12=Label(text="Sending Data\n Please Wait . . .")
    text12.place(x=170,y=250, height=30, width=150)
    return

def guiDone():
    text12=Label(text="Done Processing\n Waiting for User input")
    text12.place(x=170,y=250, height=30, width=150)
    return

def guiSaveInfo():
    global info
    file_to_open = open("Original.raw","wb+")
    q=BinaryTransform(info)
    file_to_open.write(binascii.a2b_hex(q))
    return 

def guiSaveFiltered():
    global y
    file_to_open = open("Filtered.raw","wb+")
    q=BinaryTransform(y)
    file_to_open.write(binascii.a2b_hex(q))
    return 

def guiSetN():
    global N
    N=NORDER.get()
    text13=Label(text="Set Nth order:\n" +str(N))
    text13.place(x=10, y=720, height=30, width=150)
    return
    
def gui(info, Filtertype, P1, P2):
    global POT1
    global POT2
    global SCALE1
    global SCALE2
    root.title("DCAF Interface")
    

    
    frame=Frame(root, width=1400, height=1000)
    frame.pack()

    POT1=Entry(frame, width=50)
    POT2=Entry(frame, width=50)
    SCALE1=Entry(frame, width=50)
    SCALE2=Entry(frame, width=50)
    NORDER=Entry(frame, width=50)
    toolbar_frame = tk.Frame(root)
    
    button1 = Button(frame, text="LPF",command=guiLP)
    button2 = Button(frame, text="HPF", command=guiHP)
    button3 = Button(frame, text="BPF", command=guiBP)
    button4 = Button(frame, text="Play Original", command=guiPO)
    button5 = Button(frame, text="Play Filtered", command=guiPF)
    button6 = Button(frame, text="Set P1", command=guiSP1)
    button7 = Button(frame, text="Set P2", command=guiSP2)
    button8= Button(frame, text="Original", command=guiUOR)
    button9= Button(frame, text="Filtered", command=guiUFI)
    button10 = Button(frame, text="FFT", command=guiUFFT )
    button11 = Button(frame, text="PSD", command=guiUPSD)
    button12 = Button(frame, text="Phase", command=guiUPH)
    button13 = Button(frame, text="Save Original", command=guiSaveInfo)
    button14 = Button(frame, text="Save Filtered", command=guiSaveFiltered)
    button15 = Button(frame, text="Set", command=guiSetN)
    #tk.Button(root,text="HighPass",command=guiHP).grid(row=8, column=0)


    text1 = Label(text="Potentiometer 1:")
    text2 = Label(text="Potentiometer 2:")
    text3 = Label(text="Potentiometer 1:")
    text4 = Label(text=str(P1))
    text5 = Label(text="Potentiometer 2:")
    text6 = Label(text=str(P2))
    text7 = Label(text="Curent Filter: " + Filtertype)
    #text8 = Label(text=POT1.get())
    text9= Label(text="Scale from:")
    text10= Label(text="Scale to:")
    text11=Label(text="Play Time:\n 0 seconds")
    text12=Label(text="Waiting for User input")
    text13=Label(text="Set Nth order:\n")


    POT1.place(x=10,y=40,height=30, width=150)
    POT2.place(x=10,y=100,height=30, width=150)
    text1.place(x=10, y=10)
    text2.place(x=10, y=70)
    text3.place(x=170, y=10,height=30, width=150)
    text4.place(x=170, y=50,height=30, width=150)
    text5.place(x=170, y=90,height=30, width=150)
    text6.place(x=170, y=130,height=30, width=150)
    text7.place(x=170, y=170,height=30, width=150)
    text11.place(x=170, y=210, height=30, width=150)
    text12.place(x=170,y=250, height=30, width=150)
    #text8.place(x=170, y=210,height=30, width=150)
    

    #toolbar_frame.place(x = 10,y = 800,height = 30, width = 200)
    #toolbar = NavigationToolbar2TkAgg(canvas, toolbar_frame) 
    button6.place(x=10, y=140, height=30, width=75)
    button7.place(x=85, y=140, height=30, width=75)
    button1.place(x=10, y=180, height=30, width=100)
    button2.place(x=10, y=220, height=30, width=100)
    button3.place(x=10, y=260, height=30, width=100)
    button4.place(x=10, y=300, height=30, width=100)
    button5.place(x=10, y=340, height=30, width=100)
    
    text9.place(x=10, y=380)
    SCALE1.place(x=10, y=410, height=30, width=150)
    text10.place(x=10, y=450)
    SCALE2.place(x=10, y=480, height=30, width=150)
    button8.place(x=10, y=520, height=30, width=50)
    button9.place(x=60, y=520, height=30, width=50)
    button10.place(x=110, y=520, height=30, width=50)
    button11.place(x=10, y=560, height=30, width=50)
    button12.place(x=60, y=560, height=30, width=50)
    button13.place(x=10, y=600, height=30, width=75)
    button14.place(x=85, y=600, height=30, width=75)
    NORDER.place(x=10, y=660, height=30, width=150)
    text13.place(x=10, y=720, height=30, width=150)
    button15.place(x=10, y=750, height=30, width=150)
    



    #button1.place(x=10, y=10, height=30, width=100)
    #button2.place(x=10, y=50, height=30, width=100)
    #tbox1.place(x=10, y=115, height=30, width=200)
    
    fig = plt.figure(1)
    t = np.arange(0,len(info),1)
    plt.plot(t,info)
    plt.title('Original Signal')
    #-----------------------------------------------------
    fig1 = plt.figure(2)
    t = np.arange(0,len(info),1)
    plt.plot(t,info)
    plt.title('Filtered Signal')
    #-----------------------------------------------------
    fig2 = plt.figure(3)
    t = np.arange(0,len(info),1)
    plt.plot(t,info)
    plt.title('Fast Fourier Transform')
    #-----------------------------------------------------
    fig3 = plt.figure(4)
    t = np.arange(0,len(info),1)
    plt.plot(t,info)
    plt.title('original')
    #-----------------------------------------------------
    fig4 = plt.figure(5)
    t = np.arange(0,len(info),1)
    plt.plot(t,info)
    plt.title('original')
    #-----------------------------------------------------
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas1 = FigureCanvasTkAgg(fig1, master=root)
    canvas2 = FigureCanvasTkAgg(fig2, master=root)
    canvas3 = FigureCanvasTkAgg(fig3, master=root)
    canvas4 = FigureCanvasTkAgg(fig4, master=root)
    
    plot_widget = canvas.get_tk_widget()
    plot_widget1 = canvas1.get_tk_widget()
    plot_widget2 = canvas2.get_tk_widget()
    plot_widget3 = canvas3.get_tk_widget()
    plot_widget4 = canvas4.get_tk_widget()
    
    plot_widget.place(x=390,y=10,width= 1100,height = 190)
    plot_widget1.place(x=390,y=210,width= 1100,height = 190)
    plot_widget2.place(x=390,y=410,width= 1100,height = 190)
    plot_widget3.place(x=390,y=610,width= 1100,height = 190)
    plot_widget4.place(x=390,y=810,width= 1100,height = 190)
        
        
def Main():   
    global Filtertype
    global timeOfsample
    global N
    global x
    global fftx
    global psd
    global y
    global freqs
    global h
    global x
    global w
    
    while ser.in_waiting:
        mode=ser.read()
        
        if (mode=="0"): #stop recording button
            global info
            global contents
            global N
            #guiReceiving()
            contents=serialread(x);
            info=IntegerTransform(contents);
            global SCALE1A
            SCALE1A=0
            global SCALE2A
            SCALE2A=len(info)
            plotInfo()

            if(Filtertype=='lowpass'):
                global y            
                y=LowPass(N,p1,44100,info);

            if(Filtertype=='highpass'):
                global y
                y=HighPass(N,p1,44100,info);

            if(Filtertype=='bandpass'):
                global y

                y=BandPass(N,p1,p2,44100,info);
            guiTIME()
            SCALE2A=len(y)
            plotFiltered()
            SCALE2A=len(info)
            plotFFTInfo()
            SCALE2A=len(y)
            plotFFTFiltered()
            SCALE2A=len(info)
            plotOther2()
            #guiSending()
            info2=BinaryTransform(y)
            #gui(info,fftx,freqs,psd,y,p1,p2,w,h,Filtertype) 
            print('kk')
            ser.write(binascii.a2b_hex(info2));
            #guiDone()
            print('done')
        if('1'==mode):
            #Filtertype='lowpass'
            guiLP()
            print('lowpass')
            
        if('2'==mode):
            #Filtertype='highpass'
            guiHP()
            print('highpass')
            
        if('3'==mode):
            #Filtertype='bandpass'
            guiBP()
            print('bandpass')
            
        if ('4'==mode):
            global p1
            p1=str()
            while ser.in_waiting:
                p1=p1+ser.read();
            guiP1()
            print('p1: ')
            print(p1);
            
        if('5'==mode):
            global p2
            p2=str()
            while ser.in_waiting:
                p2=p2+ser.read();
            guiP2()
            print('p2: ')
            print(p2);
    root.after(1,Main)
root = Tk()
gui(info, Filtertype, p1, p2)  
Main()
root.after(1, Main)
root.mainloop()