# =====================================
# Creado por Sergio Leonel Villegas
# INTI - Departamento de Metrología Cuántica
# Programa: Termohigómetro Plutón THB
# =====================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, date
import calendar
import re
from datetime import datetime

# Obtener fecha y hora actual
ahora = datetime.now()
# Armar nombre de archivo con formato dd_mm_dd_hh_mm_ss
nombre_archivo = "Filtrado_datos__" + ahora.strftime("%d_%m_%d_%H_%M_%S") + ".txt"

# ==========================
# --- Config de datos ---
# ==========================
ARCHIVO = Path("Temperatura y Humedad-data-2025-08-22 17_20_33.csv")
ENCODING = "latin1"  # si hiciera falta, probar "cp1252"

# ==========================
# Utilidades
# ==========================
def to_float_clean(x):
    s = str(x)
    s = re.sub(r"[^0-9.\-]", "", s)
    return float(s) if s not in ("", None, "") else pd.NA

def remove_outliers_iqr(df_in, column):
    if df_in.empty:
        return df_in
    Q1 = df_in[column].quantile(0.25)
    Q3 = df_in[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return df_in[(df_in[column] >= lower) & (df_in[column] <= upper)]

# ==========================
# Calendario (widget)
# ==========================
class CalendarWidget(ttk.Frame):
    """Calendario simple clickeable (sin dependencias externas)."""
    def __init__(self, master, initial_date=None, on_change=None, **kwargs):
        super().__init__(master, **kwargs)

        # Estilos para botones de día
        self.style = ttk.Style(self)
        # Estilo base
        self.style.configure("Cal.Day.TButton", padding=2)
        # Estilo seleccionado (intentamos darle relieve y fuente bold)
        self.style.configure("Cal.Selected.TButton", padding=2)
        self.style.map("Cal.Selected.TButton",
                       relief=[("!disabled", "sunken")])

        # Estado
        init = initial_date if isinstance(initial_date, date) else (
            initial_date.date() if isinstance(initial_date, datetime) else datetime.now().date()
        )
        self.selected = init
        self.view_year = self.selected.year
        self.view_month = self.selected.month
        self.on_change = on_change  # callback al cambiar

        header = ttk.Frame(self)
        header.pack(fill="x", pady=4)

        self.prev_btn = ttk.Button(header, text="⟵", width=3, command=self.prev_month)
        self.prev_btn.pack(side="left")

        self.title_var = tk.StringVar()
        self.title_lbl = ttk.Label(header, textvariable=self.title_var, font=("Segoe UI", 10, "bold"))
        self.title_lbl.pack(side="left", expand=True)

        self.next_btn = ttk.Button(header, text="⟶", width=3, command=self.next_month)
        self.next_btn.pack(side="right")

        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(pady=2)

        headers = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]
        for i, d in enumerate(headers):
            ttk.Label(self.grid_frame, text=d, width=3, anchor="center").grid(row=0, column=i)

        self.day_buttons = []
        for r in range(1, 7):
            for c in range(7):
                b = ttk.Button(self.grid_frame, text="", width=3, style="Cal.Day.TButton",
                               command=lambda rr=r, cc=c: self.on_day_click(rr, cc))
                b.grid(row=r, column=c, padx=1, pady=1)
                self.day_buttons.append(b)

        self.refresh()

    def refresh(self):
        self.title_var.set(f"{calendar.month_name[self.view_month]} {self.view_year}")
        cal = calendar.Calendar(firstweekday=0)  # Lunes
        month_days = cal.monthdayscalendar(self.view_year, self.view_month)

        for b in self.day_buttons:
            b.config(text="", state="disabled", style="Cal.Day.TButton")

        # Llenar
        idx = 0
        for week in month_days:
            for d in week:
                b = self.day_buttons[idx]
                if d != 0:
                    # marcado de seleccionado
                    if (self.view_year, self.view_month, d) == (self.selected.year, self.selected.month, self.selected.day):
                        b.config(text=f"[{d}]", state="normal", style="Cal.Selected.TButton")
                    else:
                        b.config(text=str(d), state="normal", style="Cal.Day.TButton")
                idx += 1

    def on_day_click(self, r, c):
        idx = (r - 1) * 7 + c
        text = self.day_buttons[idx].cget("text")
        if text:
            # sacar corchetes si están
            try:
                day = int(text.strip("[]"))
            except ValueError:
                day = int(text)
            self.selected = self.selected.replace(year=self.view_year, month=self.view_month, day=day)
            self.refresh()
            if callable(self.on_change):
                self.on_change()

    def next_month(self):
        if self.view_month == 12:
            self.view_month = 1
            self.view_year += 1
        else:
            self.view_month += 1
        self.refresh()

    def prev_month(self):
        if self.view_month == 1:
            self.view_month = 12
            self.view_year -= 1
        else:
            self.view_month -= 1
        self.refresh()

    def get_date(self):
        return self.selected

# ==========================
# Selector de fecha-hora (calendario + spinboxes)
# ==========================
class DateTimeInterval(ttk.Frame):
    def __init__(self, master, label_text, initial_dt=None, on_change=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_change = on_change
        ttk.Label(self, text=label_text, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=6, pady=(0,4), sticky="w")

        init = initial_dt or datetime.now().replace(microsecond=0, second=0)
        self.calendar = CalendarWidget(self, initial_date=init, on_change=self._notify_change)
        self.calendar.grid(row=1, column=0, columnspan=6, pady=2)

        ttk.Label(self, text="Hora:").grid(row=2, column=0, sticky="e")
        self.h_var = tk.StringVar(value=f"{init.hour:02d}")
        self.m_var = tk.StringVar(value=f"{init.minute:02d}")
        self.s_var = tk.StringVar(value=f"{init.second:02d}")

        self.h_spin = ttk.Spinbox(self, from_=0, to=23, width=3, textvariable=self.h_var, format="%02.0f")
        self.m_spin = ttk.Spinbox(self, from_=0, to=59, width=3, textvariable=self.m_var, format="%02.0f")
        self.s_spin = ttk.Spinbox(self, from_=0, to=59, width=3, textvariable=self.s_var, format="%02.0f")

        self.h_spin.grid(row=2, column=1, padx=2)
        ttk.Label(self, text=":").grid(row=2, column=2)
        self.m_spin.grid(row=2, column=3, padx=2)
        ttk.Label(self, text=":").grid(row=2, column=4)
        self.s_spin.grid(row=2, column=5, padx=2)

        # Disparar on_change cuando cambian hh/mm/ss
        for w in (self.h_spin, self.m_spin, self.s_spin):
            w.bind("<KeyRelease>", lambda e: self._notify_change())
            w.bind("<FocusOut>", lambda e: self._notify_change())

        # Label grande con el datetime actual de este panel
        self.display_var = tk.StringVar(value=self._fmt_dt(self.get_datetime()))
        ttk.Label(self, textvariable=self.display_var,
                  font=("Segoe UI", 10, "bold")).grid(row=3, column=0, columnspan=6, pady=(6,0), sticky="w")

    def _fmt_dt(self, dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _notify_change(self):
        # Actualiza texto local y notifica al exterior
        self.display_var.set(self._fmt_dt(self.get_datetime()))
        if callable(self.on_change):
            self.on_change()

    def get_datetime(self):
        d = self.calendar.get_date()
        try:
            h = int(self.h_var.get())
            m = int(self.m_var.get())
            s = int(self.s_var.get())
        except ValueError:
            h,m,s = 0,0,0
        return datetime(d.year, d.month, d.day, h, m, s)

# ==========================
# App principal
# ==========================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Filtro Ambiental | Calendario, Hora y Temperatura")
        self.geometry("1060x720")
        self.minsize(1020, 680)

        # Panel superior: intervalos y filtros
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        now = datetime.now().replace(microsecond=0)
        self.dt_inicio = DateTimeInterval(top, "Inicio", now - timedelta(days=1), on_change=self.update_selected_labels)
        self.dt_fin    = DateTimeInterval(top, "Fin", now, on_change=self.update_selected_labels)
        self.dt_inicio.pack(side="left", padx=10)
        self.dt_fin.pack(side="left", padx=10)

        # Banda de visualización clara de INICIO / FIN
        selbar = ttk.Frame(self, padding=(10,0,10,10))
        selbar.pack(fill="x", pady=(0,6))
        self.sel_inicio_var = tk.StringVar()
        self.sel_fin_var = tk.StringVar()
        ttk.Label(selbar, text="Seleccionado INICIO:", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Label(selbar, textvariable=self.sel_inicio_var, font=("Consolas", 11)).pack(side="left", padx=(6,20))
        ttk.Label(selbar, text="Seleccionado FIN:", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Label(selbar, textvariable=self.sel_fin_var, font=("Consolas", 11)).pack(side="left", padx=(6,0))

        # Controles archivo + filtros numéricos
        ctrls = ttk.Frame(self, padding=(10,0,10,10))
        ctrls.pack(fill="x", pady=(8,0))
        ttk.Label(ctrls, text="Archivo:").pack(side="left")
        self.path_var = tk.StringVar(value=str(ARCHIVO))
        ttk.Entry(ctrls, textvariable=self.path_var, width=60).pack(side="left", padx=6)
        ttk.Button(ctrls, text="Buscar...", command=self.browse_file).pack(side="left", padx=4)

        # Filtro de temperatura (min/max)
        filt = ttk.Frame(self, padding=(10,0,10,10))
        filt.pack(fill="x")
        ttk.Label(filt, text="Filtro Temperatura [°C]:").pack(side="left")
        self.tmin_var = tk.DoubleVar(value=17.0)
        self.tmax_var = tk.DoubleVar(value=26.0)
        ttk.Spinbox(filt, from_=-100, to=200, increment=0.1, width=6, textvariable=self.tmin_var).pack(side="left", padx=4)
        ttk.Label(filt, text="a").pack(side="left")
        ttk.Spinbox(filt, from_=-100, to=200, increment=0.1, width=6, textvariable=self.tmax_var).pack(side="left", padx=4)

        # Checkbox: eliminar outliers por IQR
        self.iqr_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(filt, text="Eliminar outliers por IQR", variable=self.iqr_var).pack(side="left", padx=12)

        # Botones de acción
        buttons = ttk.Frame(self, padding=(10,0,10,10))
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Aplicar filtro", command=self.aplicar_filtro).pack(side="left", padx=6)
        ttk.Button(buttons, text="Calcular promedio y desvío", command=self.calcular_stats).pack(side="left", padx=6)
        ttk.Button(buttons, text="Exportar a .txt", command=self.exportar).pack(side="left", padx=6)

        # Tabla de resultados
        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill="both", expand=True)

        cols = ("FechaHora", "Temperatura", "Humedad")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=16)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=240 if c=="FechaHora" else 170, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Estado/estadísticas
        self.stats_var = tk.StringVar(value="Datos: (sin filtrar)")
        ttk.Label(self, textvariable=self.stats_var, padding=10).pack(fill="x")

        self.df_filtrado = pd.DataFrame()
        self.df_iqr = pd.DataFrame()

        # Inicializar displays seleccionados
        self.update_selected_labels()

    # --- Helpers UI ---
    def update_selected_labels(self):
        self.sel_inicio_var.set(self.dt_inicio.get_datetime().strftime("%Y-%m-%d %H:%M:%S"))
        self.sel_fin_var.set(self.dt_fin.get_datetime().strftime("%Y-%m-%d %H:%M:%S"))

    # --- Acciones ---
    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("CSV/TXT", "*.csv *.txt"), ("Todos", "*.*")]
        )
        if path:
            self.path_var.set(path)

    def aplicar_filtro(self):
        try:
            ruta = Path(self.path_var.get())
            inicio = self.dt_inicio.get_datetime()
            fin = self.dt_fin.get_datetime()
            if fin < inicio:
                messagebox.showerror("Error", "La fecha/hora FIN no puede ser anterior a INICIO.")
                return

            tmin = float(self.tmin_var.get())
            tmax = float(self.tmax_var.get())
            if tmax < tmin:
                messagebox.showerror("Error", "Temperatura máxima no puede ser menor que la mínima.")
                return

            # Carga robusta
            df = pd.read_csv(
                ruta,
                sep=r',|\t+|\s{2,}',
                engine="python",
                header=0,
                skipinitialspace=True,
                encoding=ENCODING
            )
            # fallback si llega en una sola columna
            if df.shape[1] == 1:
                col0 = df.columns[0]
                tmp = df[col0].astype(str).str.strip()
                extra = tmp.str.extract(
                    r'^\s*([^,]+?)\s*(?:,|\t+|\s{2,})\s*([^,]+?)\s*(?:,|\t+|\s{2,})\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*$'
                )
                extra.columns = ["Humedad", "Temperatura", "time"]
                df = extra

            # limpiar headers
            df.columns = (df.columns.astype(str)
                          .str.strip()
                          .str.replace('"', '', regex=False)
                          .str.replace("'", "", regex=False))

            # mapear nombres
            rename_map = {}
            for c in df.columns:
                lc = c.lower()
                if "hum" in lc: rename_map[c] = "Humedad"
                elif "temp" in lc: rename_map[c] = "Temperatura"
                elif lc == "time": rename_map[c] = "time"
            df = df.rename(columns=rename_map)

            for needed in ["Humedad", "Temperatura", "time"]:
                if needed not in df.columns:
                    raise ValueError(f"Falta la columna requerida: {needed}")

            # parsear tiempo
            df["FechaHora"] = pd.to_datetime(
                df["time"].astype(str).str.strip(),
                format="%Y-%m-%d %H:%M:%S",
                errors="coerce"
            )
            df = df.dropna(subset=["FechaHora"])

            # aplicar ventana de tiempo
            df = df[(df["FechaHora"] >= inicio) & (df["FechaHora"] <= fin)]

            # limpieza numérica
            df["Humedad"] = df["Humedad"].apply(to_float_clean)
            df["Temperatura"] = df["Temperatura"].apply(to_float_clean)
            df = df.dropna(subset=["Humedad", "Temperatura"])

            # Filtro de temperatura por rango elegido
            df = df[(df["Temperatura"] >= tmin) & (df["Temperatura"] <= tmax)]
            self.df_filtrado = df.copy()

            # IQR (opcional)
            if self.iqr_var.get():
                antes_iqr = len(df)
                df_iqr = remove_outliers_iqr(df, "Temperatura")
                df_iqr = remove_outliers_iqr(df_iqr, "Humedad")
                removidos_iqr = antes_iqr - len(df_iqr)
            else:
                df_iqr = df.copy()
                removidos_iqr = 0

            self.df_iqr = df_iqr.copy()

            # llenar tabla
            for i in self.tree.get_children():
                self.tree.delete(i)
            for _, row in df_iqr[["FechaHora", "Temperatura", "Humedad"]].iterrows():
                self.tree.insert("", "end",
                                 values=(row["FechaHora"], f"{row['Temperatura']:.4f}", f"{row['Humedad']:.4f}"))

            # estado en barra inferior
            self.stats_var.set(
                f"INICIO: {inicio.strftime('%Y-%m-%d %H:%M:%S')} | FIN: {fin.strftime('%Y-%m-%d %H:%M:%S')} | "
                f"Temp [{tmin}°C..{tmax}°C] → {len(df)} filas | "
                f"Outliers removidos (IQR): {removidos_iqr} | Resultado: {len(df_iqr)} filas"
            )

            # Aviso breve de filtros aplicados
            messagebox.showinfo(
                "Filtro aplicado",
                (
                    f"Intervalo:\n  {inicio}  →  {fin}\n"
                    f"Rango de temperatura: {tmin}°C a {tmax}°C\n"
                    f"Outliers por IQR: {'eliminados' if self.iqr_var.get() else 'NO eliminados'}\n\n"
                    f"Filas resultantes: {len(self.df_iqr)}"
                )
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def calcular_stats(self):
        if self.df_iqr.empty:
            messagebox.showwarning("Sin datos", "No hay datos filtrados. Aplicá el filtro primero.")
            return

        t_mean = self.df_iqr["Temperatura"].mean()
        t_std  = self.df_iqr["Temperatura"].std()
        h_mean = self.df_iqr["Humedad"].mean()
        h_std  = self.df_iqr["Humedad"].std()
        n_val  = len(self.df_iqr)

        messagebox.showinfo(
            "Promedio y Desvío (datos filtrados)",
            (
                f"n = {n_val}\n\n"
                f"Temperatura:\n  Promedio = {t_mean:.6g}\n  Desv. estándar = {t_std:.6g}\n\n"
                f"Humedad:\n  Promedio = {h_mean:.6g}\n  Desv. estándar = {h_std:.6g}"
            )
        )

    def exportar(self):
        if self.df_iqr.empty:
            messagebox.showwarning("Aviso", "No hay datos filtrados para exportar. Aplicá el filtro primero.")
            return
        try:
            out_path = Path(nombre_archivo)
            self.df_iqr[["FechaHora", "Temperatura", "Humedad"]].to_csv(out_path, index=False, sep="\t")
            messagebox.showinfo("OK", f"Exportado a {out_path.resolve()}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = App()
    app.mainloop()
