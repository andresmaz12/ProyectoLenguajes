import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class FormularioPrincipal:
    def __init__(self):
        pass

    # ================== Función para crear la tabla ==================
    def crear_tabla():
        """Genera la tabla de tokens"""
        if not tokens_dict:
            return
        
        canvas = tk.Canvas(frame_tabla, bg="white")
        scrollbar_v = tk.Scrollbar(frame_tabla, orient="vertical", command=canvas.yview)
        scrollbar_h = tk.Scrollbar(frame_tabla, orient="horizontal", command=canvas.xview)
        
        frame_interno = tk.Frame(canvas, bg="white")
        frame_interno.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=frame_interno, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        columnas = ["TOKEN", "TIPO", "CANTIDAD"]
        for col, texto in enumerate(columnas):
            lbl = tk.Label(frame_interno, text=texto, bg="#2c3e50", fg="white", 
                        width=25, font=("Arial", 10, "bold"), borderwidth=1, relief="solid")
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        tokens_ordenados = sorted(tokens_dict.items(), key=lambda x: (x[1]["Tipo"], x[0]))
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
    def seleccionar_archivo(self):
        """Permite al usuario seleccionar un archivo"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo a analizar",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            ruta_archivo.set(archivo)
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()
                self.text_contenido.config(state=tk.NORMAL)
                self.text_contenido.delete(1.0, tk.END)
                self.text_contenido.insert(tk.END, contenido)
                self.text_contenido.config(state=tk.DISABLED)
                
                nombre_archivo = os.path.basename(archivo)
                self.ventana.title(f"Analizador Léxico y Gramatical - {nombre_archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ No se pudo leer el archivo: {str(e)}")

    # ================== Interfaz gráfica ==================
    ventana = tk.Tk()
    ventana.title("Analizador Léxico y Gramatical")
    ventana.geometry("1200x700")
    ventana.configure(bg="#34495e")

    ruta_archivo = tk.StringVar()

    frame_izq = tk.Frame(ventana, bg="#34495e")
    frame_izq.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    frame_der = tk.Frame(ventana, bg="#34495e")
    frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    tk.Label(frame_izq, text="CÓDIGO FUENTE", bg="#34495e", fg="white", 
            font=("Arial", 12, "bold")).pack(pady=5)

    frame_botones = tk.Frame(frame_izq, bg="#34495e")
    frame_botones.pack(pady=5)

    btn_seleccionar = tk.Button(frame_botones, text="📁 Seleccionar", 
                                command=seleccionar_archivo, bg="#3498db", fg="white",
                                font=("Arial", 10, "bold"), padx=15, pady=8)
    btn_seleccionar.pack(side="left", padx=5)

    btn_analizar = tk.Button(frame_botones, text="🔍 Analizar", 
                            command=analizar_archivo, bg="#2ecc71", fg="white",
                            font=("Arial", 10, "bold"), padx=15, pady=8)
    btn_analizar.pack(side="left", padx=5)

    text_contenido = scrolledtext.ScrolledText(frame_izq, wrap="none", width=50, height=35, 
                                            borderwidth=2, relief="solid", font=("Consolas", 10),
                                            state=tk.DISABLED)
    text_contenido.pack(fill="both", expand=True, pady=5)

    tk.Label(frame_der, text="ANÁLISIS LÉXICO Y GRAMATICAL", bg="#34495e", fg="white",
            font=("Arial", 12, "bold")).pack(pady=5)

    text_mensajes = scrolledtext.ScrolledText(frame_der, wrap="word", width=60, height=10,
                                            borderwidth=2, relief="solid", font=("Arial", 9),
                                            state=tk.DISABLED)
    text_mensajes.pack(fill="both", expand=False, pady=5)

    tk.Label(frame_der, text="TABLA DE TOKENS", bg="#34495e", fg="white",
            font=("Arial", 12, "bold")).pack(pady=5)

    frame_tabla = tk.Frame(frame_der, bg="white", borderwidth=2, relief="solid")
    frame_tabla.pack(fill="both", expand=True, pady=5)

    ventana.mainloop()