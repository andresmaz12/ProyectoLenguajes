import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os

class InterfazAnalizador:
    """Interfaz gráfica del analizador léxico y gramatical"""
    
    def __init__(self, analizador_lexico, analizador_gramatical):
        """
        Inicializa la interfaz
        
        Args:
            analizador_lexico: Instancia de AnalizadorLexico
            analizador_gramatical: Instancia de AnalizadorGramatical
        """
        self.analizador_lexico = analizador_lexico
        self.analizador_gramatical = analizador_gramatical
        
        self.ventana = tk.Tk()
        self.ventana.title("Analizador Léxico y Gramatical")
        self.ventana.geometry("1200x700")
        self.ventana.configure(bg="#34495e")
        
        self.ruta_archivo = tk.StringVar()
        
        self._construir_interfaz()
    
    def _construir_interfaz(self):
        """⚠ SE MANTIENE IGUAL EL DISEÑO - Construye todos los elementos de la interfaz"""
        
        # ===== PANELES PRINCIPALES =====
        frame_izq = tk.Frame(self.ventana, bg="#34495e")
        frame_izq.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        frame_der = tk.Frame(self.ventana, bg="#34495e")
        frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # ===== PANEL IZQUIERDO (CÓDIGO FUENTE) =====
        tk.Label(frame_izq, text="CÓDIGO FUENTE", bg="#34495e", fg="white", 
                font=("Arial", 12, "bold")).pack(pady=5)
        
        # Botones
        frame_botones = tk.Frame(frame_izq, bg="#34495e")
        frame_botones.pack(pady=5)
        
        btn_seleccionar = tk.Button(frame_botones, text="📂 Seleccionar", 
                                    command=self._seleccionar_archivo, 
                                    bg="#3498db", fg="white",
                                    font=("Arial", 10, "bold"), 
                                    padx=15, pady=8)
        btn_seleccionar.pack(side="left", padx=5)
        
        btn_analizar = tk.Button(frame_botones, text="🔍 Analizar", 
                                command=self._analizar_codigo_textbox,  # ⚠ NUEVA FUNCIÓN
                                bg="#2ecc71", fg="white",
                                font=("Arial", 10, "bold"), 
                                padx=15, pady=8)
        btn_analizar.pack(side="left", padx=5)

        # ===== PANEL DERECHO (RESULTADOS) =====
        tk.Label(frame_der, text="ANÁLISIS LÉXICO Y GRAMATICAL", bg="#34495e", fg="white",
                font=("Arial", 12, "bold")).pack(pady=5)

        # Área de mensajes
        self.text_mensajes = scrolledtext.ScrolledText(
            frame_der, wrap="word", width=60, height=10,
            borderwidth=2, relief="solid", font=("Arial", 9),
            state=tk.DISABLED
        )
        self.text_mensajes.pack(fill="both", expand=False, pady=5)

        tk.Label(frame_der, text="TABLA DE TOKENS", bg="#34495e", fg="white",
        font=("Arial", 12, "bold")).pack(pady=5)

        # Frame para la tabla
        self.frame_tabla = tk.Frame(frame_der, bg="white", borderwidth=2, relief="solid")
        self.frame_tabla.pack(fill="both", expand=True, pady=5)

        # Área de texto editable
        self.text_contenido = scrolledtext.ScrolledText(
            frame_izq, wrap="none", width=50, height=35, 
            borderwidth=2, relief="solid", font=("Consolas", 10),
            state=tk.NORMAL  # ⚠ CAMBIO IMPORTANTE: ahora editable
        )
        self.text_contenido.pack(fill="both", expand=True, pady=5)

    def _seleccionar_archivo(self):
        """⚠ SE MANTIENE IGUAL - Permite al usuario seleccionar un archivo"""
        archivo = filedialog.askopenfilename(
        title="Seleccionar archivo a analizar",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
        if archivo:
            self.ruta_archivo.set(archivo)
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    
                self.text_contenido.config(state=tk.NORMAL)
                self.text_contenido.delete(1.0, tk.END)
                self.text_contenido.insert(tk.END, contenido)
                self.text_contenido.config(state=tk.DISABLED)
                    
                # Mostrar nombre del archivo en el título
                nombre_archivo = os.path.basename(archivo)
                self.ventana.title(f"Analizador Léxico y Gramatical - {nombre_archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"⚠ No se pudo leer el archivo: {str(e)}")
        
    def _analizar_archivo(self):
        """
        ⚠ CAMBIO PRINCIPAL: Ahora usa los analizadores en lugar de lógica embebida
        Analiza el archivo seleccionado
        """
        if not self.ruta_archivo.get():
            messagebox.showwarning("Atención", "⚠️ Seleccione un archivo primero")
            return
        
        ruta = self.ruta_archivo.get()
        if not os.path.exists(ruta):
            messagebox.showerror("Error", f"⚠ El archivo {ruta} no existe")
            return
        
        # Limpiar resultados anteriores
        self._limpiar_resultados()
        
        try:
            # Leer el código
            with open(ruta, "r", encoding="utf-8") as archivo:
                codigo = archivo.read()
            
            # ⚠ CAMBIO: Análisis separado en módulos
            # Análisis léxico
            resultado_lexico = self.analizador_lexico.analizar_codigo(codigo)
            
            # Análisis gramatical
            resultado_gramatical = self.analizador_gramatical.analizar_codigo(codigo)
            
            # Mostrar resultados
            self._mostrar_resultados(resultado_lexico, resultado_gramatical)
            
            # Crear tabla de tokens
            self._crear_tabla()
            
        except Exception as e:
            messagebox.showerror("Error", f"⚠ Error al analizar el archivo: {str(e)}")
    
    def _limpiar_resultados(self):
        """Limpia el área de mensajes y la tabla"""
        self.text_mensajes.config(state=tk.NORMAL)
        self.text_mensajes.delete(1.0, tk.END)
        self.text_mensajes.config(state=tk.DISABLED)
        
        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
    
    def _mostrar_resultados(self, resultado_lexico, resultado_gramatical):
        """
        ⚠ SE MANTIENE IGUAL EL FORMATO - Muestra los resultados del análisis
        """
        self.text_mensajes.config(state=tk.NORMAL)
        
        # Configurar estilos
        self.text_mensajes.tag_config("error", foreground="red", font=("Arial", 9, "bold"))
        self.text_mensajes.tag_config("warning", foreground="orange", font=("Arial", 9, "bold"))
        self.text_mensajes.tag_config("exito", foreground="green", font=("Arial", 10, "bold"))
        
        # Mostrar errores léxicos
        if resultado_lexico['errores_lexicos']:
            for error in resultado_lexico['errores_lexicos']:
                self.text_mensajes.insert(tk.END, error['mensaje'] + "\n", "error")
        
        # Mostrar errores gramaticales
        if resultado_gramatical['errores']:
            for error in resultado_gramatical['errores']:
                self.text_mensajes.insert(tk.END, error + "\n", "error")
        
        # Mostrar advertencias
        if resultado_gramatical['advertencias']:
            for adv in resultado_gramatical['advertencias']:
                self.text_mensajes.insert(tk.END, adv + "\n", "warning")
        
        # Mensaje de éxito si no hay errores
        if not resultado_lexico['errores_lexicos'] and not resultado_gramatical['errores']:
            self.text_mensajes.insert(tk.END, "✓ Análisis exitoso sin errores\n", "exito")
        
        # Resumen
        total_errores = len(resultado_lexico['errores_lexicos']) + len(resultado_gramatical['errores'])
        total_advertencias = len(resultado_gramatical['advertencias'])
        
        self.text_mensajes.insert(tk.END, f"\n📊 RESUMEN:\n", "exito")
        self.text_mensajes.insert(tk.END, f"   • Errores: {total_errores}\n", 
                                 "error" if total_errores > 0 else "exito")
        self.text_mensajes.insert(tk.END, f"   • Advertencias: {total_advertencias}\n", 
                                 "warning" if total_advertencias > 0 else "exito")
        self.text_mensajes.insert(tk.END, f"   • Tokens únicos: {len(resultado_lexico['tokens'])}\n", "exito")
        self.text_mensajes.insert(tk.END, f"   • Variables: {len(resultado_gramatical['variables'])}\n", "exito")
        self.text_mensajes.insert(tk.END, f"   • Funciones: {len(resultado_gramatical['funciones'])}\n", "exito")
        
        self.text_mensajes.config(state=tk.DISABLED)
    
    def _crear_tabla(self):
        """⚠ SE MANTIENE IGUAL - Genera la tabla de tokens"""
        tokens_dict = self.analizador_lexico.tokens_dict
        
        if not tokens_dict:
            return
        
        # Crear canvas con scrollbar
        canvas = tk.Canvas(self.frame_tabla, bg="white")
        scrollbar_v = tk.Scrollbar(self.frame_tabla, orient="vertical", command=canvas.yview)
        scrollbar_h = tk.Scrollbar(self.frame_tabla, orient="horizontal", command=canvas.xview)
        
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
        tokens_ordenados = self.analizador_lexico.obtener_tokens_ordenados()
        
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

    def _analizar_codigo_textbox(self):
        """Analiza el contenido escrito directamente en el TextBox"""
        codigo = self.text_contenido.get("1.0", tk.END).strip()
        if not codigo:
            messagebox.showwarning("Atención", "⚠️ No hay código para analizar")
            return

        # Limpiar resultados anteriores
        self._limpiar_resultados()

        try:
            # ⚙ Análisis léxico y gramatical
            resultado_lexico = self.analizador_lexico.analizar_codigo(codigo)
            resultado_gramatical = self.analizador_gramatical.analizar_codigo(codigo)

            # Mostrar resultados
            self._mostrar_resultados(resultado_lexico, resultado_gramatical)
            self._crear_tabla()

        except Exception as e:
            messagebox.showerror("Error", f"⚠ Error al analizar el código: {str(e)}")

    def iniciar(self):
        """Inicia el loop principal de la interfaz"""
        self.ventana.mainloop()