# DAQ setup
# JH@KrappLab
# 2016-08-02: DAQ setup
# 2016-08-03: DAQ thread
#
#=============================================
from PyDAQmx import *

import time
import numpy
import scipy.io
import matplotlib.pyplot as plt
import threading

##########################
class JH_DAQ():
    #analog_input = Task()  
      
    def __init__(self, Channel = 2.0 ,name = "Dev1/ai0:1", Fs = 20000.0, Duration = 1.0):
        self.Fs=Fs          # Hz
        self.Duration = Duration      # Seconds
        self.Channel = Channel       # Lines
        self.datalen = int(self.Fs*self.Duration*self.Channel)

        self.analog_input = Task()
        self.read = int32()
        self.data = numpy.zeros((self.datalen,), dtype=numpy.float64)

        self.analog_input.CreateAIVoltageChan(name,"",
                                 DAQmx_Val_Cfg_Default,-10.0,10.0,
                                 DAQmx_Val_Volts,None)
        self.analog_input.CfgSampClkTiming("",self.Fs,
                                      DAQmx_Val_Rising,
                                      DAQmx_Val_FiniteSamps,
                                      self.datalen)

    def rec(self):
        # DAQmx Start Code
        print 'Data acquiring...'
        #analog_input.StartTask()
        self.analog_input.StartTask()
        # DAQmx Read Code
        timeout = 20.0
        self.analog_input.ReadAnalogF64(int(self.Fs*self.Duration),
                           timeout,DAQmx_Val_GroupByChannel,self.data,
                           self.datalen,byref(self.read),None)

        print "Acquired %d samples"%self.read.value
        self.data=numpy.transpose(numpy.split(self.data,self.Channel))

    def plot(self):
        t=numpy.linspace(0,self.Duration,self.Fs*self.Duration)
        #print len(t)
        #print len(self.data)
        plt.figure()
        plt.subplot(211)
        plt.plot(t,self.data[:,0])
        plt.subplot(212)
        plt.plot(t,self.data[:,1],'r')
        plt.show()   

    def log(self, note='[memo]'):
        scipy.io.savemat('[Raw][' + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '][2Ch][H1]'+note, {'data':self.data}) 
        pass  

##########################

class JH_DAQ_Thread(threading.Thread):
    def __init__(self, Channel = 2.0 ,name = "Dev1/ai0:1", Fs = 20000.0, Duration = 1.0,memo='[memo]',log=1):
        threading.Thread.__init__(self)
        self.Fs=Fs          # Hz
        self.Duration = Duration      # Seconds
        self.Channel = Channel       # Lines
        self.datalen = int(self.Fs*self.Duration*self.Channel)
        self.memo=memo
        self.log = log

        self.analog_input = Task()
        self.read = int32()
        self.data = numpy.zeros((self.datalen,), dtype=numpy.float64)

        self.analog_input.CreateAIVoltageChan(name,"",
                                 DAQmx_Val_Cfg_Default,-10.0,10.0,
                                 DAQmx_Val_Volts,None)
        self.analog_input.CfgSampClkTiming("",self.Fs,
                                      DAQmx_Val_Rising,
                                      DAQmx_Val_FiniteSamps,
                                      self.datalen)
    def run(self):
        # DAQmx Start Code
        print 'Data acquiring...'
        #analog_input.StartTask()
        self.analog_input.StartTask()
        # DAQmx Read Code
        timeout = 20.0
        self.analog_input.ReadAnalogF64(int(self.Fs*self.Duration),
                           timeout,DAQmx_Val_GroupByChannel,self.data,
                           self.datalen,byref(self.read),None)

        print "Acquired %d samples"%self.read.value
        self.data=numpy.transpose(numpy.split(self.data,self.Channel))
        if self.log == 1:
            scipy.io.savemat('[Raw][' + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '][2Ch]'+self.memo, {'data':self.data}) 
        
        
##########################

if __name__ == "__main__":

    daq = JH_DAQ(Duration=10)
    daq.rec()
    #daq.log(note='[S30]')
    daq.plot()
