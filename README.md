# INTI instrumentation

Collection of Python programs developed for INTI to automate and log measurements from various laboratory instruments.

## Overview

This repository contains measurement automation tools organized by experiment type and instrument class. All Dash-based applications use the standard Python web framework for real-time data visualization and logging.

### Quick Start for Dash Applications

To run any Dash program:
1. Open command prompt (or Anaconda Prompt, or Terminal)
2. Navigate to the program folder
3. Run `python NAME_OF_YOUR_PROGRAM.py`
4. Open your browser and navigate to `http://localhost:8050`

Programs must end with:
```python
if __name__ == '__main__':
    app.run_server(debug=True)
```

---

## Programs by Category

### 1. QHE Measurements (`QHE_meas/`)

Quantum Hall Effect measurement systems using Dash for real-time data acquisition and visualization.

#### **KEI2661_dash.py**
- **Purpose**: Current-voltage characterization using Keithley 6221
- **Instruments**: Keithley 6221 (current source)
- **Features**: Real-time I-V curve plotting, current sweep automation
- **How to run**: `python KEI2661_dash.py`

#### **KEI2661_Agilent34401_dash.py**
- **Purpose**: Automated I-V measurements with simultaneous voltage and current monitoring
- **Instruments**: 
  - Keithley 6221 (current source)
  - HP 34401 (digital multimeter)
- **Features**: Dual-channel measurement, automated sweeps, data logging to CSV
- **How to run**: `python KEI2661_Agilent34401_dash.py`

#### **CriticalCurrent/** (folder)
- Programs for critical current measurements in superconducting samples

---

### 2. Temperature and Humidity Monitoring (`termohigrometro/`)

Arduino-based data logger with web interface for temperature and humidity measurements.

#### **Overview**
- Logs data from Arduino via serial connection
- Real-time plotting with Dash
- CSV export for data analysis

#### **How to Run**

**Option 1: Direct Python execution**
```bash
pip install -r requirements.txt
python app.py
```
Then open `http://localhost:8050` in your browser.

**Option 2: Using batch file (Windows)**
```bash
run_app.bat
```

#### **Key Features**
1. **COM Port Selection**: Choose which serial port your Arduino is connected to
2. **File Path Configuration**: Specify where to save CSV data
3. **Start/Stop Controls**: Button to begin and end measurements
4. **Real-time Plotting**: Live graph updates as data arrives
5. **Data Export**: Automatic CSV logging

#### **Project Structure**
```
termohigrometro/
├── app.py                          # Main Dash application
├── readme.md                       # Detailed documentation
├── run_app.bat                    # Windows batch launcher
├── requirements.txt               # Python dependencies
├── frontend/                      # Frontend components
├── backend/                       # Backend logic
├── viejo/                        # Previous versions
└── data/
    └── data.csv                  # Logged measurements
```

#### **Dependencies**
- `dash` - Web framework
- `dash-bootstrap-components` - UI components
- `pandas` - Data manipulation
- `plotly` - Plotting
- `pyserial` - Arduino communication

---

### 3. Transport Measurements (`transport_meas/`)

Shubnikov-de Haas (SdH) oscillations and transport property characterization.

#### **SdH_dos_anillos_autoscale_rev3.py**
- **Purpose**: Measure Shubnikov-de Haas oscillations in two-ring geometry
- **Instruments**: 
  - Keithley 6221 (current source)
  - SR830 Lock-in Amplifier
  - Custom two-ring measurement setup
- **Features**: Automatic scaling, magnetic field sweep, oscillation detection
- **How to run**: `python SdH_dos_anillos_autoscale_rev3.py`

#### **Vtp_dos_anillos_autoscale_varVheater_rev1.py**
- **Purpose**: Transport measurements with variable heater voltage control
- **Instruments**: Same as SdH plus heater power supply control
- **Features**: Temperature-dependent transport, variable heating
- **How to run**: `python Vtp_dos_anillos_autoscale_varVheater_rev1.py`

#### **respuesta_freq_cuatro_lockin.py**
- **Purpose**: Frequency response measurements using four lock-in amplifiers
- **Instruments**: 4× SR830 Lock-in Amplifiers, signal generator
- **Features**: Multi-channel phase and amplitude response, frequency sweep
- **How to run**: `python respuesta_freq_cuatro_lockin.py`

#### **SR830pythonClass_rev2.py**
- **Purpose**: Python class interface for SR830 lock-in amplifier
- **Features**: GPIB/serial communication, parameter control, data acquisition
- **Usage**: Import as module in other scripts

#### **Ametek7124.py**
- **Purpose**: Interface for Ametek 7124 lock-in amplifier
- **Features**: Alternative lock-in control

#### **SignalRecovery7280.py**
- **Purpose**: Interface for Signal Recovery 7280 lock-in amplifier
- **Features**: Alternative lock-in control

---

### 4. Instrument Drivers (`Instruments/`)

Reusable Python classes and control scripts for laboratory instruments.

#### **SR830pythonClass_rev4.py**
- **Purpose**: Comprehensive SR830 lock-in amplifier control class
- **Features**: 
  - Full parameter control (frequency, amplitude, time constant, etc.)
  - Data acquisition
  - Phase/amplitude measurement
- **Usage**: 
  ```python
  from SR830pythonClass_rev4 import SR830
  lockin = SR830(address='GPIB0::8::INSTR')
  voltage = lockin.read_voltage()
  ```

#### **V_vs_freq_SRS830_rev4.py**
- **Purpose**: Frequency response measurement script using SR830
- **Features**: Automated frequency sweep, voltage amplitude logging
- **How to run**: `python V_vs_freq_SRS830_rev4.py`

#### **Keithley/** (folder)
Advanced Keithley instrument drivers and measurement scripts.

**Keithley/6430 Electrometer/**
- Automation for Keithley 6430 electrometer in measurement mode
- Features:
  - Index-based quantity selection (Voltage/Current/Resistance)
  - 10-reading acquisition with timestamped save
  - Demo mode for testing without hardware
  - Audible alert on completion
- Usage:
  ```bash
  python Electrometer.py           # Normal operation
  python Electrometer.py --demo    # Demo mode
  ```

---

### 5. Testing and Examples (`pruebas/`)

Example code and prototypes for development.

#### **InstrumentoClass.py**
- Base class template for instrument control
- Demonstrates instrument interface design patterns

#### **dash_front_end_example.py**
- Simple Dash application example
- Starting template for new web-based measurement tools

#### **ejemplo_dash.py**
- Spanish-language Dash example
- Basic data plotting and user interaction

#### **measured.csv**
- Sample measurement data for testing

---

## Dependencies by Project

### General (all projects)
```
python >= 3.7
```

### Dash Applications (QHE_meas, termohigrometro)
```
dash >= 2.0
dash-bootstrap-components
pandas
plotly
pyserial
```

### Transport Measurements & Instrument Control
```
pyvisa          # GPIB/serial instrument communication
pyvisa-py       # Pure Python VISA backend (alternative to NI-VISA)
pandas
numpy
matplotlib      # For some plotting applications
```

### Installation
```bash
# Install all dependencies
pip install -r requirements.txt
```

Or for specific projects:
```bash
# For QHE measurements
pip install dash dash-bootstrap-components pandas plotly pyserial

# For transport measurements
pip install pyvisa pyvisa-py pandas numpy matplotlib
```

---

## Instrument Connection Guide

### GPIB (IEEE-488)
Used by: Keithley 6221, HP 34401, SR830, Signal Recovery, Ametek instruments
- Requires GPIB interface card or USB-GPIB adapter
- Use PyVISA with NI-VISA or pyvisa-py backend

### Serial (RS-232/USB)
Used by: Arduino (termohigrometro), some lock-ins
- Connection via COM port (Windows) or /dev/tty* (Linux)
- Specify port in program (e.g., `COM3`, `/dev/ttyUSB0`)

### USB
Used by: Various modern instruments
- Direct USB connection, typically shows as COM port or GPIB resource

---

## Common Troubleshooting

### GPIB Connection Issues
```python
import pyvisa
rm = pyvisa.ResourceManager()
print(rm.list_resources())  # List connected instruments
```

### Serial/Arduino Connection Issues
- Check device manager (Windows) or `ls /dev/tty*` (Linux)
- Verify baud rate matches Arduino sketch
- Ensure pyserial is installed: `pip install pyserial`

### Dash Applications Not Starting
- Verify port 8050 is not in use
- Check Python path and dependencies
- Run with: `python app.py --debug` for verbose output

### Lock-in Amplifier Communication
- Verify GPIB address (usually GPIB0::n::INSTR where n=device number)
- Check instrument is powered on and GPIB is enabled
- Use VISA test utility to verify connection

---

## Contributing

When adding new programs:
1. Create appropriate folder if needed (QHE_meas, transport_meas, Instruments, etc.)
2. Include a detailed docstring in the Python file
3. Add requirements.txt if new dependencies are needed
4. Update this README.md with:
   - Program name and purpose
   - Instruments used
   - How to run instructions
   - Key features

---

## License

MIT License - See LICENSE file for details.

---

## Repository Structure Summary

```
INTI_instrumentacion/
├── README.md                          # This file
├── LICENSE
├── QHE_meas/                          # Quantum Hall Effect measurements
│   ├── KEI2661_dash.py
│   ├── KEI2661_Agilent34401_dash.py
│   ├── CriticalCurrent/
│   └── readme.md
├── termohigrometro/                   # Temperature/humidity logger
│   ├── app.py
│   ├── readme.md
│   ├── run_app.bat
│   ├── requirements.txt
│   ├── backend/
│   ├── frontend/
│   ├── data/
│   └── viejo/
├── transport_meas/                    # Transport properties (SdH, etc.)
│   ├── SdH_dos_anillos_autoscale_rev3.py
│   ├── Vtp_dos_anillos_autoscale_varVheater_rev1.py
│   ├── respuesta_freq_cuatro_lockin.py
│   ├── SR830pythonClass_rev2.py
│   ├── Ametek7124.py
│   └── SignalRecovery7280.py
├── Instruments/                       # Reusable instrument drivers
│   ├── SR830pythonClass_rev4.py
│   ├── V_vs_freq_SRS830_rev4.py
│   └── Keithley/
│       └── 6430 Electrometer/
│           ├── Electrometer.py
│           ├── README.md
│           └── requirements.txt
└── pruebas/                           # Testing and examples
    ├── InstrumentoClass.py
    ├── dash_front_end_example.py
    ├── ejemplo_dash.py
    └── measured.csv
```

---

**Last updated**: 2026-05-14  
**Maintainer**: realmariano
