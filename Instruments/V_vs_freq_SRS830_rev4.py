# V_vs_freq_SRS830.py
# Date: 2026
# Author: Integrado

import pyvisa
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import json
import numpy as np
import pandas as pd

from datetime import datetime

from SR830pythonClass_rev4 import SR830 as sr830

import threading
import queue
import os

# =========================
# INSTRUMENTO
# =========================
rm = pyvisa.ResourceManager()
equipos = rm.list_resources()
print('Equipos conectados:', equipos)

lia3obj = rm.open_resource('GPIB0::8::INSTR')
inst = sr830(lia3obj)

print(inst.get_identity())

v_excitation = 0.15
inst.set_amplitude(v_excitation)
inst.set_harmonic(1)
time.sleep(2)

# =========================
# PARÁMETROS
# =========================
freq_start_exp = 1
freq_end_exp = 5
num_points = 100

freqs = np.logspace(freq_start_exp, freq_end_exp, num=num_points)


def get_time_constant(freq):
    tau = 1 / (20 * freq)
    return max(0.03, min(tau, 10))  # límites del instrumento



# =========================
# PATHS Y ARCHIVOS
# =========================
base_path = 'E:/Python Scripts/INTI_instrumentacion/SRS830/'
os.makedirs(base_path, exist_ok=True)

now = datetime.now()
str_file = now.strftime('%Y%m%d_%H%M%S') + '_barrido_freq'

csv_file = os.path.join(base_path, str_file + '.dat')
h5_file = os.path.join(base_path, str_file + '.h5')
json_file = os.path.join(base_path, str_file + '_conf.json')

# CSV header
with open(csv_file, 'w') as f:
    f.write('timestamp FREQ X Y R\n')

# HDF5 store
store = pd.HDFStore(h5_file, mode='w')

# =========================
# COLA Y DATOS
# =========================
data_queue = queue.Queue()

f_vals = []
X_vals = []
Y_vals = []
R_vals = []

# =========================
# WORKER
# =========================
def acquisition_worker(freqs, q):

    inst.auto_scale()
    time.sleep(2)

    for f in freqs:

        # ---- set frecuencia ----
        inst.set_frequency(f)

        # ---- set constante de tiempo ----
        tau_target = get_time_constant(f)
        tau_real = inst.set_time_constant(tau_target)

        # ---- ajustar sensibilidad automáticamente ----
        inst.adjust_sensitivity()

        # ---- esperar estabilización ----
        for _ in range(2):
            inst.adjust_sensitivity()
            inst.wait_settle(2)

        # ---- medir ----
        X, Y, R = inst.measure(settle=False)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f'[Worker] f={f:.2f} Hz | tau={tau_real:.3e} | X={X:.2e} | Y={Y:.2e}')

        # enviar a la cola
        q.put((f, X, Y, R))

        # -------- CSV incremental --------
        with open(csv_file, 'a') as f_out:
            f_out.write(f"{timestamp} {f:.6e} {X:.6e} {Y:.6e} {R:.6e}\n")

        # -------- HDF5 incremental --------
        df_row = pd.DataFrame({
            'timestamp': [timestamp],
            'freq': [f],
            'X': [X],
            'Y': [Y],
            'R': [R]
        })

        store.append('data', df_row, format='table', data_columns=True)

    q.put(None)
    print("Worker terminado")



# =========================
# GRÁFICO
# =========================
fig, ax = plt.subplots(1, 3)

lineX, = ax[0].plot([], [], 'g.-', label='X')
lineY, = ax[1].plot([], [], 'g.-', label='Y')
lineR, = ax[2].plot([], [], 'b.-', label='R')

lines = [lineX, lineY, lineR]

titles = ['X vs frequency', 'Y vs frequency', 'R vs frequency']
for i in range(3):
    ax[i].set_title(titles[i])
    ax[i].set_xlabel('Frequency (Hz)')
    ax[i].set_ylabel('V (V)')
    ax[i].legend()

finished = False

# =========================
# UPDATE (SOLO GRAFICA)
# =========================
def update(frame):
    global finished

    while not data_queue.empty():
        item = data_queue.get()

        if item is None:
            print("Adquisición finalizada")
            finished = True
            continue

        f, X, Y, R = item

        f_vals.append(f)
        X_vals.append(X)
        Y_vals.append(Y)
        R_vals.append(R)

    data = [X_vals, Y_vals, R_vals]

    for i, line in enumerate(lines):
        line.set_data(f_vals, data[i])

    for a in ax:
        a.relim()
        a.autoscale_view()

    # detener animación pero dejar ventana abierta
    if finished:
        ani.event_source.stop()

    return lines

# =========================
# LANZAR THREAD
# =========================
worker_thread = threading.Thread(
    target=acquisition_worker,
    args=(freqs, data_queue),
    daemon=True
)
worker_thread.start()

# =========================
# ANIMACIÓN
# =========================
ani = FuncAnimation(
    fig,
    update,
    interval=200,
    blit=False
)

plt.show()

# =========================
# FINALIZACIÓN
# =========================
worker_thread.join()
store.close()

print("Guardado finalizando...")

# -------- DataFrame final --------
df = pd.DataFrame({
    'timestamp': [now.strftime('%Y-%m-%d %H:%M:%S')] * len(f_vals),
    'FREQ': f_vals,
    'X': X_vals,
    'Y': Y_vals,
    'R': R_vals
})

df.to_csv(os.path.join(base_path, str_file + '_final.dat'),
          sep=' ', index=False)

# -------- CONFIG JSON --------
config_data = {
    'fecha-hora': now.strftime('%Y-%m-%d %H:%M:%S'),
    'frequency_start_exp': freq_start_exp,
    'frequency_end_exp': freq_end_exp,
    'num_points': num_points,
    'voltage (V)': v_excitation,
    'instrument': inst.get_identity(),
    'mode': inst.get_mode(),
    'sensitivity': inst.get_full_scale(inst.get_sensitivity()),
    'time_constant': inst.get_time_constant()
}

with open(json_file, 'w') as f:
    json.dump(config_data, f, indent=4)

print("Todo guardado correctamente")