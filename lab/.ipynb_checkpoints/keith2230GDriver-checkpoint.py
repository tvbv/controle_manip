#================================================================================================
# this is a library enabling remote control of a keithley 2230G with a gpib port from a pc
#
# develloped @ C2N, freely inspired by https://github.com/Aaron-Mott/Keithley-2230G/blob/master/2230G.py
#
#Need a pyvisa backend to work
#
#Check that the driver for the gpib to usb cable are downloaded on your computer 
#
#================================================================================================

import pyvisa as visa
import time

class Keith2230G():
    
    def __init__(self, adress, backend = '@ivi', reset = 0 ,silence_initial_measurements=0):
        """
        Initializes the instrument with instrument address, backend to use with pyvisa,reset and silencing initial measurements
        ----------
        inst_address : str
            The port address of the instrument.
        backend : str
            Backend to use for pyvisa
        reset : bool
            resets every parameters to default setup (see 4-11 on keithley manual) and set every channel to 0V and 0A
        silence_initial_measurements :bool
            to silence 
        """

        self.adress = adress
        self.ressource_manager = visa.ResourceManager(backend)
        self.inst = self.ressource_manager.open_resource(self.adress)
        self.inst.write("SYST:REM \n") #put the keithley in remote mode
        
        if reset:
            self.inst.write("*RST \n")
            for i in ['CH1','CH2','CH3']:
                self.set_channel_voltage(i,0)
                self.set_channel_current(i,0)
        
        print("Connected Device : " + self.inst.query("*IDN? \n"))
        
        if not(silence_initial_measurements):
            self.reality_check()
        
        
    
    def get_channel(self):
        """Queries selected channel."""
        channel = self.inst.query("INST?\n")
        return(channel)
    
    def get_channel_current(self, channel):
        """
        Queries the current reading on the specified channel.
        Parameters
        ----------
        channel : str
            The selected channel or channels with the current readings to
            return. can be CH1, CH2, CH3 or ALL
        """
        if channel in ['CH1','CH2','CH3','ALL']:
            reading = self.inst.query(f"FETC:CURR? {channel}\n")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")
        return(reading)
    
    def get_channel_voltage(self, channel):
        """
        Queries the voltage reading on the specified channel.
        Parameters
        ----------
        channel : str
            The selected channel or channels with the voltage readings to
            return. can be CH1, CH2, CH3 or ALL.
        """
        if channel in ['CH1','CH2','CH3','ALL']:
            volt = self.inst.query(f"FETC:VOLT? {channel}\n")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")
        return(volt)
    
    def get_channel_current_set(self, channel):
        """
        Queries the current set on the specified channel.
        Parameters
        ----------
        channel : str
            The selected channel or channels with the current set to
            return. can be CH1, CH2, CH3 or ALL
        """
        if channel in ['CH1','CH2','CH3','ALL']:
            self.inst.write(f"INST:SEL {channel}\n")
            reading = self.inst.query("SOUR:CURR?\n")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")
        return(reading)
    
    def get_channel_voltage_set(self, channel):
        """
        Queries the voltage set on the specified channel.
        Parameters
        ----------
        channel : str
            The selected channel or channels with the voltage set to
            return. can be CH1, CH2, CH3 or ALL.
        """
        if channel in ['CH1','CH2','CH3','ALL']:
            self.inst.write(f"INST:SEL {channel}\n")
            volt = self.inst.query("SOUR:VOLT?\n")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")
        return(volt)
    
    def set_channel_current(self, channel, curr):
        """
        set the current on the specified channel.
        Parameters
        ----------
        channel : str
            The selected channel or channels with the current readings to
            return. can be CH1, CH2 or CH3.
        curr : the current in Amps
        """
           
        if channel in ['CH1','CH2','CH3']:
            self.inst.write(f"INST:SEL {channel}\n")
            self.inst.write(f"SOUR:CURR {curr} A\n")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")
            
    def set_channel_voltage(self, channel, volt):
        """
        set the voltage on the specified channel.
        Parameters
        ----------
        channel : str
            The selected channel or channels with the voltage level to
            set. can be CH1, CH2 or CH3.
        voltage : the voltage in Volts
        """
        if channel in ['CH1','CH2','CH3']:
            self.inst.write(f"INST:SEL {channel}\n")
            if channel == 'CH3' and volt>6.1:
                raise  ValueError("Value Error. Please enter a voltage below 6.1 for channel 3.")
            else:
                self.inst.write(f"SOUR:VOLT {volt} V\n")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")
    
    def set_channel_output(self, channel, state):
        """
        set the output state on the specified channel.
        Parameters
        ----------
        channel : str
            The selected channel or channels with the voltage level to
            set. can be CH1, CH2 or CH3.
        state : 0 for no ouptut, 1 for ouptuting
        """
        

        if channel in ['CH1','CH2','CH3']:
            self.inst.write(f"INST:SEL {channel}\n")
            if state in [0,1]:
                self.inst.write(f"SOUR:CHAN:OUTP {state}\n")
            else:
                raise ValueError("Value Error. Please enter a valid output state")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")
    
    def reality_check(self):
        """
        Print the set and measured current and voltage of every channel.
        ----------
        """
        for i in ['CH1','CH2','CH3']:
            print("=====\n"+"Channel : "+i[2]+"; Set voltage = "+self.get_channel_voltage_set(i)+"; Set Current = "+self.get_channel_current_set(i)+"\nMeasured voltage  = "+self.get_channel_voltage(i)+"; Measured current = "+self.get_channel_current(i))
        print("=====")
    
    def channel_reality_check(self,channel):
        """
        Print the set and measured current and voltage of a specified channel.
        ----------
        channel : str
            The selected channel.
        """
        if channel in ['CH1','CH2','CH3']:
            print("=====\n"+"Channel : "+channel[2]+"\nSet voltage = "+self.get_channel_voltage_set(channel)+"\nSet Current = "+self.get_channel_current_set(channel)+"\nMeasured voltage  = "+self.get_channel_voltage(channel)+"\nMeasured current = "+self.get_channel_current(channel))
        print("=====")
        
    def close(self):
        self.inst.write('SYST:LOC')
        self.inst.close()
        