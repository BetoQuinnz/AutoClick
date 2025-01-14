import tkinter as tk
from tkinter import messagebox
import ctypes
from ctypes import wintypes
from pynput import keyboard
import threading
import time
import pyautogui  
import random

running = False
click_interval = 0.1
stop_key = keyboard.Key.f1
selected_monitor = None


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def centrar_ventana(ventana):
    ventana.update_idletasks()
    ancho = ventana.winfo_width()
    alto = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana.winfo_screenheight() // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

class MonitorInfo:
    def __init__(self):
        self.monitores = []
        self.obtener_monitores()

    def obtener_monitores(self):
        user32 = ctypes.windll.user32
        monitors = []

        def monitor_enum_proc(hmonitor, hdc_monitor, lprc_monitor, dw_data):
            rect = ctypes.cast(lprc_monitor, ctypes.POINTER(wintypes.RECT)).contents
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            monitors.append((rect.left, rect.top, width, height))
            return True

        monitor_enum_proc_t = ctypes.WINFUNCTYPE(
            wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM
        )
        monitor_enum_proc_c = monitor_enum_proc_t(monitor_enum_proc)
        user32.EnumDisplayMonitors(None, None, monitor_enum_proc_c, 0)
        self.monitores = monitors

    def mostrar_monitores(self):
        return [f"Monitor {i + 1}: {w}x{h} @ ({x}, {y})" for i, (x, y, w, h) in enumerate(self.monitores)]

monitor_info = MonitorInfo()

def actualizar_estado(label, mensaje):
    label.config(text=f"Estado: {mensaje}")

def iniciar_autoclicker():
    global running, click_interval
    if selected_monitor is None:
        messagebox.showwarning("Autoclicker", "Por favor, seleccione una pantalla antes de iniciar el autoclicker.")
        return

    if running:
        messagebox.showwarning("Autoclicker", "El autoclicker ya está en ejecución.")
        return

    try:
        interval = float(interval_entry.get())
        if interval <= 0:
            raise ValueError
        click_interval = interval
    except ValueError:
        messagebox.showerror("Error", "El tiempo debe ser un número válido mayor a 0.")
        return

    running = True
    actualizar_estado(estado_label, "En ejecución")
    threading.Thread(target=start_autoclick, daemon=True).start()
    threading.Thread(target=keyboard_listener, daemon=True).start()


def detener_autoclicker():
    global running
    running = False
    actualizar_estado(estado_label, "Detenido")


def keyboard_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def on_press(key):
    global running
    if key == stop_key:
        running = False
        actualizar_estado(estado_label, "Detenido desde teclado")
        return False


def start_autoclick():
    global running, click_interval
    monitor = monitor_info.monitores[selected_monitor]
    monitor_x, monitor_y, monitor_width, monitor_height = monitor

    while running:

        click_x = random.randint(monitor_x, monitor_x + monitor_width - 1)
        click_y = random.randint(monitor_y, monitor_y + monitor_height - 1)


        pyautogui.moveTo(click_x, click_y)
        pyautogui.click()


        actualizar_estado(estado_label, f"Haciendo clic en monitor {selected_monitor + 1} en posición ({click_x}, {click_y})")

        time.sleep(click_interval)

def seleccionar_monitor(event, monitor_id):
    global selected_monitor
    selected_monitor = monitor_id
    actualizar_estado(estado_label, f"Monitor {monitor_id + 1} seleccionado")

def crear_interfaz():
    global interval_entry, estado_label
    ventana = tk.Tk()
    ventana.title("Autoclicker")
    ventana.geometry("600x500")
    ventana.configure(bg="black")
    ventana.resizable(False, False)

    centrar_ventana(ventana)

    tk.Label(ventana, text="Tiempo entre clics (segundos):", bg="black", fg="white").pack(pady=10)
    interval_entry = tk.Entry(ventana)
    interval_entry.insert(0, "0.1")
    interval_entry.pack(pady=5)

    button_frame = tk.Frame(ventana, bg="black")
    button_frame.pack(pady=10)

    detener_btn = tk.Button(button_frame, text="Detener", command=detener_autoclicker, bg="red", fg="white")
    detener_btn.grid(row=0, column=0, padx=10)

    iniciar_btn = tk.Button(button_frame, text="Iniciar", command=iniciar_autoclicker, bg="green", fg="white")
    iniciar_btn.grid(row=0, column=1, padx=10)

    pantalla_frame = tk.Frame(ventana, bg="gray", bd=2, relief="sunken")
    pantalla_frame.pack(pady=20, fill="both", expand=True, padx=10)

    monitores = monitor_info.mostrar_monitores()
    for i, monitor in enumerate(monitores):
        monitor_canvas = tk.Canvas(pantalla_frame, width=100, height=50, bg="lightgray", highlightthickness=1, highlightbackground="black")
        monitor_canvas.place(relx=(i + 1) / (len(monitores) + 1), rely=0.5, anchor="center")
        monitor_canvas.create_text(50, 25, text=f"Pantalla {i + 1}", fill="black")
        monitor_canvas.bind("<Button-1>", lambda event, monitor_id=i: seleccionar_monitor(event, monitor_id))

    output_frame = tk.Frame(ventana, bg="black")
    output_frame.pack(pady=10, fill="x")

    estado_label = tk.Label(output_frame, text="Estado: Listo", bg="black", fg="white", anchor="w")
    estado_label.pack(fill="x", padx=10)

    ventana.mainloop()

if __name__ == "__main__":
    crear_interfaz()
