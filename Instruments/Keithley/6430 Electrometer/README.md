# Keithley 6430 Electrometer — Automation Script

Python script for **automatic measurements** with the **Keithley 6430** in **measurement mode**.  
You select the quantity via an **index** (0/1/2), configure the range **manually** on the instrument (e.g., set **20 V** to measure ~**19 V**), and the program **logs 10 readings** into a **timestamped `.txt` file**. A **buzzer sound** is played at the end to indicate completion.

## Features
- Index-based quantity selection:
  - `0` → Voltage
  - `1` → Current
  - `2` → Resistance
- Manual instrument setup (range, protection, etc.) on the front panel.
- Automatic acquisition of **10 measurements**.
- Auto-save to **timestamped text file**.
- **Audible buzzer** at the end of the run.
- Optional **demo mode** (`--demo`) to test without hardware.

## Requirements
- Python 3.x
- [PyVISA](https://pyvisa.readthedocs.io/)
- VISA backend (e.g., NI-VISA or `pyvisa-py`)

> On Windows, the buzzer uses `winsound` (built-in).

## Installation
```bash
# from this folder: Keithley/6430 Electrometer/
pip install -r requirements.txt
```

If you don’t have NI-VISA installed, you can try with `pyvisa-py`:
```bash
pip install pyvisa pyvisa-py
```

## Usage

### Normal (with instrument)
```bash
python Electrometer.py
```
- Set the **index** in the script (0/1/2) to choose V/I/Ω.
- Configure the instrument **manually** (e.g., set 20 V range for ~19 V).
- The script takes **10 readings**, saves a `.txt` with a timestamp, and plays a buzzer at the end.

### Demo (no hardware required)
```bash
python Electrometer.py --demo
```
Prints **simulated readings** so you can test the workflow without a 6430 connected.

## Output
Example filename:
```
2025-08-26_14-35-10.txt
```
Example content:
```
Range: 20 V
Measurement: Voltage
Readings (10):
19.001
19.003
...
```

## Folder structure
```
Keithley/
└── 6430 Electrometer/
    ├── Electrometer.py
    ├── README.md
    └── requirements.txt
```

## Troubleshooting
- **`visa not found` / backend issues**: install NI-VISA or try `pyvisa-py`.
- **No sound**: on non-Windows systems, replace `winsound` by `print("\a")` or another cross-platform audio solution.
- **Permission/driver**: make sure the 6430 is visible in VISA with:
  ```python
  import pyvisa
  rm = pyvisa.ResourceManager()
  print(rm.list_resources())
  ```

## License
MIT (inherited from the repository).
