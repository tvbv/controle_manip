# **lab library for lab appliances control**

To use, put the lab folder in the folder where your python code/jupyter notebook lies and use  `import lab ` as you would for a classic python package. please follow the following instructions to have a working library.

**Library needed and versions used for the dev:**

-**develloped on python 3.6.13 |Anaconda, Inc.| (default, Mar 16 2021, 12:57:03) [MSC v.1916 32 bit (Intel)]**

-**Numpy version  1.19.2**

-**Comtypes version 1.1.7**

-**Pyvisa version  1.11.3**

## **How to install the drivers**

install **pyvisa** library at https://anaconda.org/conda-forge/pyvisa or with the installer of your choice. 
_please note that you'll need to install a VISA backend, more information here:https://pyvisa.readthedocs.io/en/latest/introduction/configuring.html_

install **numpy**,**matlplotlib** and **comtypes**

## **keith2230GDriver**

Import with  `from lab import keith2230GDriver`. This driver enables the control of the keithley 2230G generator via a usb-to-gpib adapter.

## **keys204ADriver**

Import with  `from lab import keys204ADriver `. This driver enables the control of the keysight 204A scope via a RJ45 cable.

One can find the keysight scope's doc regarding remote control here: https://keysight-docs.s3-us-west-2.amazonaws.com/keysight-pdfs/DSOV084A/Programmer_s+Guide+for+Infiniium+Oscilloscop.pdf



