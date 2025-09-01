import numpy as np
import pyvisa
import time
import struct
from datetime import datetime

'''
# ==============================================================
# IMPORTANT:
# - Modify the variable "index" below:
#       0 → Voltage source mode
#       1 → Current source mode
# - Adjust the "rangos_v" or "rangos_i" lists according to
#   the desired measurement ranges.
# - Adjust the "time.sleep()" values for the desired waiting time.
# ============================================================== 

'''



##########################################################################


index=1 # =0 voltage source, =1 current source
# ==== Initial Configuration ====
rangos_i = [         '1E-3', '-1E-3', '10E-3', '-10E-3', '100E-3', '-100E-3']
rangos_v = [         '100e-3','-100e-3','1E1', '-1E1', '10E1', '-10E1']
measurement_time=10  # seconds


###########################################################################
if index==0:
    rangos=rangos_v
    units ='Volt'
    parameter='VOLT'
    parameter2='CURR'
    protection= ':SENS:CURR:PROT 105e-3'          # Voltage protection at 20 V
else:
    rangos=rangos_i
    units ='Ampere'
    parameter='CURR'
    parameter2='VOLT'
    protection= ':SENS:VOLT:PROT 21'          # Voltage protection at 20 V
    
rm = pyvisa.ResourceManager()

Keithley = rm.open_resource('GPIB0::26::INSTR')

# Terminations
Keithley.write_termination = '\n'
Keithley.read_termination = '\n'

# Check communication
print('Keithley:',Keithley.query('*IDN?')) 

Keithley.write('*RST')
time.sleep(2)

# === Start of measurements ===
for rango in rangos:
    print(f"\nRANGE: {float(rango):.4f} {units}\n")

    # Configure source
    #Keithley.write('*RST')                           # Reset the instrument
    Keithley.write(':SOUR:FUNC ' + parameter )                 # Select CURRENT source
    Keithley.write(':SOUR:'+  parameter +':MODE FIXED')        # Fixed current mode
    Keithley.write(':SENS:FUNC "' + parameter2 +'"')           # Measurement of current
    Keithley.write(':SYST:AZER ON')                           #
    Keithley.write(':SOUR:'+ parameter +':LEV '+ rango)        # Measurement of current
    Keithley.write(protection)          #   Current protection at 105 mA or voltage protection at 21 V            
    Keithley.write(':OUTP ON')                     # Turn output ON
    

    rango_abs=abs(float(rango))
    time.sleep (measurement_time)  

# === Close instruments ===
Keithley.write(':OUTP OFF')                        # Turn output OFF
rm.close()



    