import time
import numpy as np

class SR830:

    TIME_CONSTANTS_SEC = [
        10e-6, 30e-6, 100e-6, 300e-6,
        1e-3, 3e-3, 10e-3, 30e-3,
        100e-3, 300e-3,
        1, 3, 10, 30,
        100, 300,
        1e3, 3e3,
        1e4, 3e4
    ]

    SENSITIVITY_FULL_SCALE = [
        2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9,
        1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6,
        500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3,
        200e-3, 500e-3, 1
    ]

    VISA_DELAY = 0.02

    def __init__(self, lockin, debug=False):
        self.lockin = lockin
        self.debug = debug

    # =========================
    # LOW LEVEL
    # =========================
    def _write(self, cmd):
        if self.debug:
            print(f"[WRITE] {cmd}")
        self.lockin.write(cmd)
        time.sleep(self.VISA_DELAY)

    def _query(self, cmd, retries=3):
        for i in range(retries):
            try:
                if self.debug:
                    print(f"[QUERY] {cmd}")
                resp = self.lockin.query(cmd)
                time.sleep(self.VISA_DELAY)
                return resp
            except Exception as e:
                if "VI_ERROR_TMO" in str(e):
                    print(f"[RETRY {i+1}] {cmd}")
                    time.sleep(0.2)
                else:
                    raise
        raise Exception(f"Query failed: {cmd}")

    # =========================
    # IDENTIDAD
    # =========================
    def get_identity(self):
        return self._query('*IDN?').strip()

    # =========================
    # FRECUENCIA
    # =========================
    def set_frequency(self, freq):
        self._write(f'FREQ {freq}')

    def get_frequency(self):
        return float(self._query('FREQ?'))
    
    # =========================
    # HARMONIC
    # =========================
    def set_harmonic(self, harmonic):
        self._write(f'HARM {harmonic}')
        print('Harmonic set to {}'.format(harmonic))

    # =========================
    # TIME CONSTANT
    # =========================
    def get_time_constant(self):
        idx = int(self._query('OFLT?'))
        return self.TIME_CONSTANTS_SEC[idx]

    def set_time_constant(self, tau):
        idx = min(range(len(self.TIME_CONSTANTS_SEC)),
                  key=lambda i: abs(self.TIME_CONSTANTS_SEC[i] - tau))
        self._write(f'OFLT {idx}')
        return self.TIME_CONSTANTS_SEC[idx]

    # =========================
    # SENSITIVIDAD
    # =========================
    def get_sensitivity(self):
        return int(self._query('SENS?'))

    def set_sensitivity(self, idx):
        idx = max(0, min(idx, len(self.SENSITIVITY_FULL_SCALE)-1))
        self._write(f'SENS {idx}')

    def get_full_scale(self):
        return self.SENSITIVITY_FULL_SCALE[self.get_sensitivity()]

    # =========================
    # MEDICIONES
    # =========================
    def read_x(self):
        return float(self._query('OUTP? 1'))

    def read_y(self):
        return float(self._query('OUTP? 2'))

    def read_xy(self):
        x = self.read_x()
        y = self.read_y()
        return x, y

    def read_r(self):
        return float(self._query('OUTP? 3'))

    def measure(self, settle=True, n_tau=5):
        if settle:
            self.wait_settle(n_tau)

        x, y = self.read_xy()
        r = np.sqrt(x**2 + y**2)
        return x, y, r

    # =========================
    # AUTO SCALE
    # =========================
    def auto_scale(self):
        self._write('AGAN')
        time.sleep(2)

    # =========================
    # WAIT
    # =========================
    def wait_settle(self, n_tau=5):
        tau = self.get_time_constant()
        wait_time = n_tau * tau
        if self.debug:
            print(f"[WAIT] {wait_time:.2f}s")
        time.sleep(wait_time)

    # =========================
    # AUTO SENS (MEJORADO)
    # =========================
    def adjust_sensitivity(self):
        idx = self.get_sensitivity()
        full_scale = self.get_full_scale()

        x, y = self.read_xy()
        r = np.sqrt(x**2 + y**2)

        ratio = r / full_scale

        if ratio > 0.9 and idx < len(self.SENSITIVITY_FULL_SCALE)-1:
            self.set_sensitivity(idx + 1)
            self.wait_settle(3)

        elif ratio < 0.1 and idx > 0:
            self.set_sensitivity(idx - 1)
            self.wait_settle(3)


    # =========================
    # AMPLITUD
    # =========================   
    def set_amplitude(self, voltage):
        self._write(f'SLVL {voltage}')
        time.sleep(1)