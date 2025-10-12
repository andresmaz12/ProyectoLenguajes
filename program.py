import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import re
import os

# ================== Cargar JSON de tokens ==================
tokens_json = {}
try:
    with open("Tokens.json", "r", encoding="utf-8") as archivo:
        tokens_json = json.load(archivo)
    print("✓ JSON de tokens cargado correctamente")
except FileNotFoundError:
    print("❌ Error: No se encontró el archivo Tokens.json")
    print("Creando archivo de ejemplo...")
    tokens_json = {
        "Preservada": ["int", "float", "char", "if", "else", "while", "for", "return", "void"],
        "operadores": ["+", "-", "*", "/", "=", "==", "!=", "<=", ">=", "<", ">", "%"],
        "signos": ["(", ")", "{", "}", ";", ","]
    }
    with open("Tokens.json", "w", encoding="utf-8") as f:
        json.dump(tokens_json, f, indent=4, ensure_ascii=False)
except json.JSONDecodeError:
    messagebox.showerror("Error", "❌ El archivo Tokens.json tiene formato inválido")
    exit()

# ================== Función para clasificar tokens ==================
def clasificar_token(token, categorias):
    """Clasifica un token según las categorías definidas en el JSON."""
    if token in categorias.get("Preservada", []):
        return "Preservada"
    if token in categorias.get("operadores", []):
        return "operadores"
    if token in categorias.get("signos", []):
        return "signos"
    if re.match(r"^\d+(\.\d+)?$", token):
        return "numeros"
    if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", token):
        return "identificadores"
    if token == " ":
        return "espacio"
    return "desconocido"

# ================== Función para analizar el archivo ==================
def analizar_archivo():
    """Analiza el archivo seleccionado y muestra errores y tabla de tokens."""
    global tokens_dict
    tokens_dict = {}

    if not ruta_archivo.get():
        messagebox.showwarning("Atención", "⚠️ Seleccione un archivo primero")
        return

    ruta = ruta_archivo.get()
    if not os.path.exists(ruta):
        messagebox.showerror("Error", f"❌ El archivo {ruta} no existe")
        return

    # Limpiar área de mensajes y tabla
    text_mensajes.config(state=tk.NORMAL)
    text_mensajes.delete(1.0, tk.END)
    for widget in frame_tabla.winfo_children():
        widget.destroy()

    errores = []
    variables_declaradas = set()
    tipos_datos = tokens_json.get("Preservada", [])

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
            
            for numero, linea in enumerate(lineas, start=1):
                linea_original = linea.rstrip()
                linea = linea.strip()
                
                if not linea or linea.startswith("//"):
                    continue

                # Separar tokens con expresiones regulares mejoradas
                tokens = re.findall(r"\w+|==|!=|<=|>=|\+\+|--|[+\-*/=<>%(){};,]", linea)

                i = 0
                esperando_identificador = False
                tipo_actual = None

                while i < len(tokens):
                    token = tokens[i]
                    categoria = clasificar_token(token, tokens_json)

                    # --- Manejo de declaraciones ---
                    if categoria == "Preservada" and token in tipos_datos:
                        esperando_identificador = True
                        tipo_actual = token

                    # --- Manejo de identificadores ---
                    elif categoria == "identificadores":
                        if esperando_identificador:
                            variables_declaradas.add(token)
                            esperando_identificador = False
                        elif token not in variables_declaradas:
                            errores.append(f"❌ Línea {numero}: Variable '{token}' usada sin declarar")

                    # Resetear si encontramos un signo de punto y coma
                    if token == ";":
                        esperando_identificador = False
                        tipo_actual = None

                    # --- Tokens desconocidos ---
                    if categoria == "desconocido":
                        errores.append(f"❌ Línea {numero}: Token desconocido '{token}'")
                    elif categoria != "espacio":
                        if token in tokens_dict:
                            tokens_dict[token]["Cantidad"] += 1
                        else:
                            tokens_dict[token] = {
                                "Token": token,
                                "Tipo": categoria,
                                "Cantidad": 1
                            }

                    i += 1

    except Exception as e:
        messagebox.showerror("Error", f"❌ Error al leer el archivo: {str(e)}")
        return

    # Mostrar errores o mensaje de éxito
    if errores:
        text_mensajes.tag_config("error", foreground="red")
        for err in errores:
            text_mensajes.insert(tk.END, err + "\n", "error")
    else:
        text_mensajes.tag_config("exito", foreground="green", font=("Arial", 10, "bold"))
        text_mensajes.insert(tk.END, "✓ Análisis completado exitosamente\n", "exito")
        text_mensajes.insert(tk.END, f"✓ Total de tokens únicos: {len(tokens_dict)}\n")
        text_mensajes.insert(tk.END, f"✓ Variables declaradas: {len(variables_declaradas)}\n")
    
    text_mensajes.config(state=tk.DISABLED)
    crear_tabla()

# ================== Función para crear la tabla ==================
def crear_tabla():
    """Genera la tabla de tokens válidos con sus tipos y cantidad."""
    if not tokens_dict:
        return
    
    # Crear canvas con scrollbar para la tabla
    canvas = tk.Canvas(frame_tabla, bg="white")
    scrollbar_v = tk.Scrollbar(frame_tabla, orient="vertical", command=canvas.yview)
    scrollbar_h = tk.Scrollbar(frame_tabla, orient="horizontal", command=canvas.xview)
    
    frame_interno = tk.Frame(canvas, bg="white")
    frame_interno.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    canvas.create_window((0, 0), window=frame_interno, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
    
    # Encabezados
    columnas = ["TOKEN", "TIPO", "CANTIDAD"]
    for col, texto in enumerate(columnas):
        lbl = tk.Label(frame_interno, text=texto, bg="#2c3e50", fg="white", 
                      width=25, font=("Arial", 10, "bold"), borderwidth=1, relief="solid")
        lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

    # Ordenar tokens por tipo y nombre
    tokens_ordenados = sorted(tokens_dict.items(), key=lambda x: (x[1]["Tipo"], x[0]))
    
    # Colores alternos para filas
    colores = ["#ecf0f1", "#ffffff"]
    
    for fila, (token, datos) in enumerate(tokens_ordenados, start=1):
        color = colores[fila % 2]
        
        tk.Label(frame_interno, text=datos["Token"], width=25, bg=color, 
                borderwidth=1, relief="solid").grid(row=fila, column=0, sticky="nsew", padx=1, pady=1)
        tk.Label(frame_interno, text=datos["Tipo"], width=25, bg=color,
                borderwidth=1, relief="solid").grid(row=fila, column=1, sticky="nsew", padx=1, pady=1)
        tk.Label(frame_interno, text=datos["Cantidad"], width=25, bg=color,
                borderwidth=1, relief="solid").grid(row=fila, column=2, sticky="nsew", padx=1, pady=1)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar_v.pack(side="right", fill="y")
    scrollbar_h.pack(side="bottom", fill="x")

# ================== Función para seleccionar archivo ==================
def seleccionar_archivo():
    """Permite al usuario seleccionar un archivo .txt y muestra su contenido."""
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo a analizar",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
    )
    if archivo:
        ruta_archivo.set(archivo)
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
            text_contenido.config(state=tk.NORMAL)
            text_contenido.delete(1.0, tk.END)
            text_contenido.insert(tk.END, contenido)
            text_contenido.config(state=tk.DISABLED)
            
            # Mostrar nombre del archivo
            nombre_archivo = os.path.basename(archivo)
            ventana.title(f"Analizador de Tokens - {nombre_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"❌ No se pudo leer el archivo: {str(e)}")

# ================== Interfaz gráfica ==================
ventana = tk.Tk()
ventana.title("Analizador Léxico")
ventana.geometry("1200x700")
ventana.configure(bg="#34495e")

# Variable global
tokens_dict = {}
ruta_archivo = tk.StringVar()

# Paneles izquierdo y derecho
frame_izq = tk.Frame(ventana, bg="#34495e")
frame_izq.pack(side="left", fill="both", expand=True, padx=10, pady=10)

frame_der = tk.Frame(ventana, bg="#34495e")
frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# ===== PANEL IZQUIERDO =====
tk.Label(frame_izq, text="CÓDIGO FUENTE", bg="#34495e", fg="white", 
         font=("Arial", 12, "bold")).pack(pady=5)

# Botones
frame_botones = tk.Frame(frame_izq, bg="#34495e")
frame_botones.pack(pady=5)

btn_seleccionar = tk.Button(frame_botones, text="📁 Seleccionar Archivo", 
                            command=seleccionar_archivo, bg="#3498db", fg="white",
                            font=("Arial", 10, "bold"), padx=15, pady=8)
btn_seleccionar.pack(side="left", padx=5)

btn_analizar = tk.Button(frame_botones, text="🔍 Analizar", 
                         command=analizar_archivo, bg="#2ecc71", fg="white",
                         font=("Arial", 10, "bold"), padx=15, pady=8)
btn_analizar.pack(side="left", padx=5)

# Área de texto con scrollbar
text_contenido = scrolledtext.ScrolledText(frame_izq, wrap="none", width=50, height=35, 
                                          borderwidth=2, relief="solid", font=("Consolas", 10),
                                          state=tk.DISABLED)
text_contenido.pack(fill="both", expand=True, pady=5)

# ===== PANEL DERECHO =====
tk.Label(frame_der, text="RESULTADOS DEL ANÁLISIS", bg="#34495e", fg="white",
         font=("Arial", 12, "bold")).pack(pady=5)

# Área de mensajes
text_mensajes = scrolledtext.ScrolledText(frame_der, wrap="word", width=60, height=10,
                                         borderwidth=2, relief="solid", font=("Arial", 9),
                                         state=tk.DISABLED)
text_mensajes.pack(fill="both", expand=False, pady=5)

tk.Label(frame_der, text="TABLA DE TOKENS", bg="#34495e", fg="white",
         font=("Arial", 12, "bold")).pack(pady=5)

# Frame para la tabla
frame_tabla = tk.Frame(frame_der, bg="white", borderwidth=2, relief="solid")
frame_tabla.pack(fill="both", expand=True, pady=5)

ventana.mainloop()