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
    
    def __init__(self, adress, backend = '@ivi',sleep_time = 0.35):
        """
        Initializes the instrument with instrument address, backend to use with pyvisa and sleep time to wait before each measure
        Parameters
        ----------
        inst_address : str
            The port address of the instrument.
        backend : str
            Backend to use for pyvisa
        sleep_time : float
            time (in secs) to wait before a measure, because of the volt and current setting inertia
        """
        self.sleep_time = sleep_time
        self.adress = adress
        self.ressource_manager = visa.ResourceManager(backend)
        self.inst = self.ressource_manager.open_resource(self.adress)
        
    def get_channel(self):
        """Queries selected channel."""
        channel = self.inst.query("INST?\n")
        return(channel)
    
    def get_channel_curr(self, channel):
        """
        Queries the current reading on the specified channel.
        Parameters
        ----------
        channel : str
            The selected channel or channels with the current readings to
            return. can be CH1, CH2, CH3 or ALL
        """
        time.sleep(self.sleep_time)
        
        if channel in ['CH1','CH2','CH3','ALL']:
            reading = self.inst.query(f"FETC:CURR? {channel}\n")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")
        return(reading)
    
    def get_channel_volt(self, channel):
        """
        Queries the voltage reading on the specified channel.
        Parameters
        ----------
        channel : str
            The selected channel or channels with the voltage readings to
            return. can be CH1, CH2, CH3 or ALL.
        """
        time.sleep(self.sleep_time)

        if channel in ['CH1','CH2','CH3','ALL']:
            volt = self.inst.query(f"FETC:VOLT? {channel}\n")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")
        return(volt)
    
    def set_channel_curr(self, channel, curr):
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
            time.sleep(self.sleep_time)
            self.inst.write(f"SOUR:CURR {curr} A\n")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")
            
    def set_channel_volt(self, channel, volt):
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
            time.sleep(self.sleep_time)
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
            time.sleep(self.sleep_time)
            if state in [0,1]:
                self.inst.write(f"OUTP:ENAB {state}\n")
            else:
                raise ValueError("Value Error. Please enter a valid output state")
        else:
            raise ValueError("Value Error. Please enter a valid channel.")