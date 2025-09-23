import tkinter as tk
from tkinter import filedialog, messagebox
import json
import re
import os

# ================== Cargar JSON de tokens ==================
tokenss = {}
try:
    with open("Tokens.json", "r", encoding="utf-8") as archivo:
        tokens_json = json.load(archivo)
    print("✓ JSON de tokens cargado correctamente")
except FileNotFoundError:
    messagebox.showerror("Error", "❌ No se encontró el archivo Tokens.json")
    exit()
except json.JSONDecodeError:
    messagebox.showerror("Error", "❌ El archivo Tokens.json tiene formato inválido")
    exit()

# ================== Función para clasificar tokens ==================
def clasificar_token(token, categorias):
    """Clasifica un token según las categorías definidas en el JSON."""
    if token in categorias["Preservada"]:
        return "Preservada"
    if token in categorias["operadores"]:
        return "operadores"
    if token in categorias["signos"]:
        return "signos"
    if re.match(r"^\d+(\.\d+)?$", token):
        return "numeros"
    if re.match(r"^[a-zA-Z][a-zA-Z0-9]*$", token):
        return "identificadores"
    if token == " ":
        return "espacio"
    return "desconocido"

# ================== Función para analizar el archivo ==================
def analizar_archivo():
    """Analiza el archivo seleccionado y muestra errores y tabla de tokens."""
    global tokenss
    tokenss = {}

    if not ruta_archivo.get():
        messagebox.showwarning("Atención", "Seleccione un archivo primero")
        return

    ruta = ruta_archivo.get()
    if not os.path.exists(ruta):
        messagebox.showerror("Error", f"El archivo {ruta} no existe")
        return

    # Limpiar área de mensajes y tabla
    text_mensajes.delete(1.0, tk.END)
    for widget in frame_tabla.winfo_children():
        widget.destroy()

    errores = []
    variables_declaradas = set()  # Guardamos las variables válidas

    with open(ruta, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()
        for numero, linea in enumerate(lineas, start=1):
            linea = linea.strip()
            if not linea:
                continue

            # Separar tokens con expresiones regulares
            tokens = re.findall(r"\w+|==|!=|<=|>=|[+\-*/=<>%(){};,]", linea)

            i = 0
            while i < len(tokens):
                token = tokens[i]
                categoria = clasificar_token(token, tokens_json)

                # --- Manejo de declaraciones ---
                if categoria == "Preservada":
                    # Si es un tipo de dato y el siguiente token es identificador → declarar variable
                    if i + 1 < len(tokens):
                        siguiente = tokens[i + 1]
                        if clasificar_token(siguiente, tokens_json) == "identificadores":
                            variables_declaradas.add(siguiente)

                # --- Manejo de identificadores ---
                elif categoria == "identificadores":
                    if token not in variables_declaradas:
                        errores.append(f"Línea {numero}: Variable '{token}' usada sin declarar")

                # --- Tokens desconocidos ---
                if categoria == "desconocido":
                    errores.append(f"Línea {numero}: Token desconocido '{token}'")
                elif categoria != "espacio":
                    if token in tokenss:
                        tokenss[token]["Cantidad"] += 1
                    else:
                        tokenss[token] = {"Token": token, "Tipo": categoria, "Cantidad": 1}

                i += 1

    # Mostrar errores o mensaje de éxito
    if errores:
        for err in errores:
            text_mensajes.insert(tk.END, err + "\n")
    else:
        text_mensajes.insert(tk.END, "✓ Todo está correcto, no se encontraron errores\n")

    crear_tabla()

# ================== Función para crear la tabla ==================
def crear_tabla():
    """Genera la tabla de tokens válidos con sus tipos y cantidad."""
    columnas = ["TOKEN", "TIPO", "CANTIDAD"]

    for col, texto in enumerate(columnas):
        lbl = tk.Label(frame_tabla, text=texto, bg="black", fg="white", width=20, borderwidth=1, relief="solid")
        lbl.grid(row=0, column=col, sticky="nsew")

    for fila, (token, datos) in enumerate(tokenss.items(), start=1):
        tk.Label(frame_tabla, text=datos["Token"], width=20, borderwidth=1, relief="solid").grid(row=fila, column=0, sticky="nsew")
        tk.Label(frame_tabla, text=datos["Tipo"], width=20, borderwidth=1, relief="solid").grid(row=fila, column=1, sticky="nsew")
        tk.Label(frame_tabla, text=datos["Cantidad"], width=20, borderwidth=1, relief="solid").grid(row=fila, column=2, sticky="nsew")

# ================== Función para seleccionar archivo ==================
def seleccionar_archivo():
    """Permite al usuario seleccionar un archivo .txt y muestra su contenido."""
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
    if archivo:
        ruta_archivo.set(archivo)
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        text_contenido.delete(1.0, tk.END)
        text_contenido.insert(tk.END, contenido)

# ================== Interfaz gráfica ==================
ventana = tk.Tk()
ventana.title("Analizador de Tokens")
ventana.geometry("1000x600")

# Paneles izquierdo y derecho
frame_izq = tk.Frame(ventana)
frame_izq.pack(side="left", fill="both", expand=True, padx=5, pady=5)

frame_der = tk.Frame(ventana)
frame_der.pack(side="right", fill="both", expand=True, padx=5, pady=5)

# Área izquierda: botones y contenido del archivo
ruta_archivo = tk.StringVar()
btn_seleccionar = tk.Button(frame_izq, text="Seleccionar Archivo", command=seleccionar_archivo)
btn_seleccionar.pack(pady=5)

btn_analizar = tk.Button(frame_izq, text="Analizar Archivo", command=analizar_archivo)
btn_analizar.pack(pady=5)

text_contenido = tk.Text(frame_izq, wrap="word", width=50, height=30, borderwidth=1, relief="solid")
text_contenido.pack(fill="both", expand=True, pady=5)

# Área derecha: mensajes y tabla
text_mensajes = tk.Text(frame_der, wrap="word", width=60, height=15, borderwidth=1, relief="solid", fg="blue")
text_mensajes.pack(fill="both", expand=False, pady=5)

frame_tabla = tk.Frame(frame_der)
frame_tabla.pack(fill="both", expand=True, pady=5)

ventana.mainloop()
