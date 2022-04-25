"""
================================================================================================
# this is a library enabling remote control of a  Keysight S series 204A with a rj45 port from a pc.
#
# develloped @ C2N, palaiseau.
#
# Need a pyvisa backend to work.
#
#================================================================================================
"""


import sys
import pyvisa as visa
import numpy as np
from comtypes.client import GetModule
from comtypes.client import CreateObject
from comtypes.automation import VARIANT
# Run GetModule once to generate comtypes.gen.VisaComLib.
if not hasattr(sys, "frozen"):
   GetModule("C:\Program Files (x86)\IVI Foundation\VISA\VisaCom\GlobMgr.dll")
import comtypes.gen.VisaComLib as VisaComLib


class Keys204A():
    """
    class that manages the scope.
    
    ...
    
    Attributes
    ----------
    adress : str
        the port adress of the scope.
    
    ressource_manager : comtypes.POINTER(IResourceManager)
        the ressource manager for the scope.
    
    inst : comtypes.POINTER(IFormattedIO488)
        comtypes instance.
    
    Methods
    ----------
    do_command(command) : 
        sends a command to the scope.
        
    do_query_string(query) :
        queries the scope and return the answer as a string.
        
    do_query_ieee_block(query) :
        enables querying easily the scope for binary data.
        
    do_query_number(query) :
        queries the scope for a number.
        
    set_trigger(trigger_channel,trigger_sweep,trigger_level) :
        set the trigger parameters.
        
    time_base(time_scale, time_ref) :
        set the time scale on the scope display.
        
    set_channels(channels, displays, y_scales, offsets, probes, input_couplings) :
        set the channels display and probes.
    
    retrieve_waveform(channel) :
        retrieve a displayed waveform on the specified channel.
    
    save_waveform(channel, name, path) : 
        retrieve and save a displayed waveform on the specified channel.
    
    
    
    """
    
    def __init__(self, adress, backend = '@ivi'):
        """
        Initializes the instrument with instrument address, backend to use with pyvisa.
        
        Parameters
        ----------
        inst_address : str
            The port address of the instrument.
        
        backend : str, default : '@ivi'
            Backend to use for pyvisa.
        """
        
        self.adress = adress
        
        self.ressource_manager = CreateObject("VISA.GlobalRM", \
        interface=VisaComLib.IResourceManager)
        self.inst = CreateObject("VISA.BasicFormattedIO", \
        interface=VisaComLib.IFormattedIO488)
        self.inst.IO = self.ressource_manager.Open(adress)
        # Clear the interface.
        self.inst.IO.Clear
        
        
        print("Connected Device : " + self.do_query_string("*IDN?"))
    
    def do_command(self,command):
        """
        enables prompting a command easily the scope.
        
        Parameters
        ----------
        command : str
            The command to send to the scope.
        """
        self.inst.WriteString("%s" % command, True)
        self.__check_instrument_errors(command)
        
    def do_query_string(self,query):
        """
        enables querying easily the scope.
        
        Parameters
        ----------
        query : str
            The query to send to the scope.
        
        Returns
        ----------
        string
        """
        self.inst.WriteString("%s" % query, True)
        result = self.inst.ReadString()
        self.__check_instrument_errors(query)
        return result
    
    def do_query_ieee_block_I2(self,query):
        """
        enables querying easily the scope for binary data.
        
        Parameters
        ----------
        query : str
            The query to send to the scope.
        
        Returns
        ----------
        list
        """
        self.inst.WriteString("%s" % query, True)
        result = self.inst.ReadIEEEBlock(VisaComLib.BinaryType_I2, \
        False, True)
        self.__check_instrument_errors(query)
        return result
    
    def do_query_number(self,query):
        """
        enables querying easily the scope for a number.
        
        Parameters
        ----------
        query : str
            The query to send to the scope.
        
        Returns
        ----------
        float
        """
        self.inst.WriteString("%s" % query, True)
        result = self.inst.ReadNumber(VisaComLib.ASCIIType_R8, True)
        self.__check_instrument_errors(query)
        return result
    
    def __check_instrument_errors(self,command):
        """
        private method, enables detection of errors.
        
        Parameters
        ----------
        command : str
            The command passed to the scope.
        """
        while True:
            self.inst.WriteString(":SYSTem:ERRor? STRing", True)
            error_string = self.inst.ReadString()
            if error_string: # If there is an error string value.
                if error_string.find("0,", 0, 2) == -1: # Not "No error".
                    print("ERROR: %s, command: '%s'" % (error_string, command))
                    print("Exited because of error.")
                    sys.exit(1)
                else: # "No error"
                    break

            else: # :SYSTem:ERRor? STRing should always return string.
                print("ERROR: :SYSTem:ERRor? STRing returned nothing, command: '%s'"% command)
                print("Exited because of error.")
                sys.exit(1)
        
    
    def set_trigger(self,trigger_channel = 1,trigger_sweep = None ,trigger_level = None, print_output = 0):
        """
        set the scope's trigger mode, level and channel.
        
        Parameters
        ----------
        trigger_channel : int, default = 1
            the channel on wich the trigger is set.
            
        trigger_sweep : str, default = None
            The type of trigger. "TRIGGERED" or "AUTO". By default no changes are applied.
        
        trigger_level : float, default = None
            the level for the trigger. By default no changes are applied.

        print_output : boolean, default = 0
            wether to prit or not the new setting to verify all is good.
        """
        
        if trigger_sweep != None:
            self.do_command(":TRIGger:SWEep "+trigger_sweep)

        self.do_command(":TRIGger:EDGE:SOURce CHANnel" + str(trigger_channel))
        
        if trigger_level !=None:
            self.do_command(":TRIGger:LEVel CHANnel" + str(trigger_channel)+","+str(trigger_level))

        
        if print_output == 1:
            qresult = self.do_query_string(":TRIGger:SWEep?")
            print("Trigger sweep: %s" % qresult)
            qresult = self.do_query_string(":TRIGger:EDGE:SOURce?")
            print("Trigger edge source: %s" % qresult)
            qresult = self.do_query_string(":TRIGger:LEVel? CHANnel"+ str(trigger_channel))
            print("Trigger level, channel" + str(trigger_channel)+": %s" % qresult)
    
    def time_base(self,time_scale, time_ref,print_output = 0):
        """
        set the scope's time base scale and offset.
        
       Parameters
        ----------
        time_scale : float
            time per division in seconds. ranges from 5e-12 to 20.
        
        time_ref : int
            percentage of the screen (starting from the left) where the time offset is put. 0 = flush left, 50 = middle , 100 = flush right.
        
        print_output : boolean, default = 0
            wether to prit or not the new setting to verify all is good.
        """
        # Set horizontal scale and offset.
        self.do_command(":TIMebase:SCALe " + str(time_scale))
        self.do_command(":TIMebase:POSition 0.0")
        self.do_command(":TIMebase:REFerence:PERCent " + str(time_ref))
        
        if print_output == 1:
            qresult = self.do_query_string(":TIMebase:SCALe?")
            print("Timebase scale: %s" % qresult)
            qresult = self.do_query_string(":TIMebase:POSition?")
            print("Timebase position: %s" % qresult)
            qresult = self.do_query_string(":TIMebase:REFerence:PERCent?")
            print(" Timebase reference percent: %s" %qresult)
    
        
    def set_channels(self, channels=[1,2,3,4], displays = [1,1,1,1], y_scales = [1,1,1,1], offsets = [0.,0.,0.,0.], probes = [None,None,None,None] , input_couplings = ['DC','DC','DC','DC'],print_output = 0):
        """
        set the scope's time base scale and offset.
        
        Parameters
        ----------
        channels : int list, default = [1,2,3,4]
            channels to tweak. 1 to 4.
        
        displays : boolean list, default = [1,1,1,1]
            displaying state of the specified channels.
        
        y_scales : int list, default = [1,1,1,1]
            voltage per division for the specifieds channels.
        
        offsets : float list, default = [0.,0.,0.,0.]
            offset for the specified channel.
        
        probes : float list, default = [None,None,None,None]
            probes ratio (X:1) for the specified channels : ranges from 1e-4 to 1e3. If probes attached are automaticaly providing the probe data to the scope, use None.
        
        input_coupling : str list, default = ['DC','DC','DC','DC']
            choose from the following parameters :
                DC = DC coupling, 1 MΩ impedance.
                DC50 or DCFifty = DC coupling, 50Ω impedance.
                AC = AC coupling, 1 MΩ impedance.
                LFR1 or LFR2 = AC 1 MΩ input impedance.
            When no probe is attached, the coupling for each channel can be AC, DC,
            DC50, or DCFifty.
            If you have an 1153A probe attached, the valid parameters are DC, LFR1, and
            LFR2 (low-frequency reject).
        
        print_output : boolean, default = 0
            wether to prit or not the new setting to verify all is good.
        """
        for i in range(len(channels)):
            c = channels[i]
            if probes[i] != None : 
                self.do_command(":CHANnel"+ str(c)+":PROBe "+str(probes[i]))
            if displays[i] != None :
                self.do_command(":CHANnel"+ str(c)+":DISPlay "+str(displays[i]))
            if y_scales[i] != None :
                self.do_command(":CHANnel" +str(c)+ ":SCALe " + str(y_scales[i]))
            
            if offsets[i] != None :
                self.do_command(":CHANnel" +str(c)+ ":OFFSet "+str(offsets[i]))
            
            if input_couplings[i] != None :
                self.do_command(":CHANnel"+ str(c)+":INPut "+ input_couplings[i])
            
            if print_output == 1:
                qresult = self.do_query_string(":CHANnel"+ str(c)+":PROBe?")
                print("Channel "+ str(c)+" probe attenuation factor: %s" % qresult)
                qresult = self.do_query_string(":CHANnel"+ str(c)+":DISPlay?")
                print("Channel "+ str(c)+" display: %s" % qresult)
                qresult = self.do_query_string(":CHANnel" +str(c)+ ":SCALe?")
                print("Channel " +str(c)+ " vertical scale: "+qresult)
                qresult = self.do_query_string(":CHANnel" +str(c)+ ":OFFSet?")
                print("Channel " +str(c)+ " offset: "+ qresult)
                qresult = self.do_query_string(":CHANnel"+str(c)+":INPut?")
                print("load imp channel" +str(c)+" : %s" %qresult)

    def retrieve_waveform(self,channel,nb_points):
        """
        retrieve y and x of the waveform on the specified channel (THEY MUST BE DISPLAYED).
        
        Parameters
        ----------
        channel : int
            number of channel to retrieve the waveform from.
        nb_points : int
            number of data points to be acquired.
        Return
        ----------
        x, y : numpy arrays
        """
        self.do_command(":ACQuire:POINts "+str(nb_points))
        self.do_command(":RUN")
        self.do_command(":WAVeform:SOURce channel"+str(channel))
        self.do_command(":WAVeform:FORMat word")
        self.do_command(":SYSTem:HEADer OFF")
        self.do_command(":WAVeform:STReaming OFF")
        number_of_points=self.do_query_string(":WAVeform:POINts?")
        y_increment = self.do_query_number(":WAVeform:YINCrement?")
        y_origin = self.do_query_number(":WAVeform:YORigin?")
        x_increment = self.do_query_number(":WAVeform:XINCrement?")
        x_origin = self.do_query_number(":WAVeform:XORigin?")
        waveform_raw = self.do_query_ieee_block_I2(":WAVeform:DATA?")

        self.do_command(":RUN")

        y_waveform = y_increment*np.array(waveform_raw) +y_origin
        x_waveform = x_increment*np.array(range(int(number_of_points)))+x_origin
        
        return x_waveform, y_waveform
    
    def save_waveform(self, channel,nb_points, name = 'waveform',path = ''):
        """
        retrieve y and x of the waveform on the specified channel (THEY MUST BE DISPLAYED) and store thame with the specified name within the specified folder.
        The data is stored under numpy array format with x being data[:,0] and y being data[:,1].
        
        Parameters
        ----------
        channel : int
            number of channel to retrieve the waveform from.
        
        nb_points : int
            number of data point to be acquired.
        
        name : str, default = 'waveform'
            name under wich data will be stored.
            
        path : str, default = ''
            path to where to store the data.
        """
        
        x,y = self.retrieve_waveform(channel,nb_points)
        data_to_store = np.stack((x,y), axis=1)
        np.save(path + name+'.npy',data_to_store)