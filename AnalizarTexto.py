import tkinter as tk
from tkinter import messagebox
import re

from Formulario import FormularioPrincipal
form = FormularioPrincipal()

class AnalisiLexico:
    def __init__(self):
        pass

    # ================== Función para clasificar tokens ==================
    def clasificar_token(self, token, categorias):
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
    tokens_dict = {}
    gramatica = GramaticaChecker()

    def analizar_archivo():
        """Analiza el archivo con validación léxica y gramatical"""
        global tokens_dict, gramatica
        tokens_dict = {}
        gramatica = GramaticaChecker()

        if not ruta_archivo.get():
            messagebox.showwarning("Atención", "⚠️ Seleccione un archivo primero")
            return

        ruta = ruta_archivo.get()
        if not os.path.exists(ruta):
            messagebox.showerror("Error", f"❌ El archivo {ruta} no existe")
            return

        text_mensajes.config(state=tk.NORMAL)
        text_mensajes.delete(1.0, tk.END)
        for widget in frame_tabla.winfo_children():
            widget.destroy()

        errores_totales = []
        advertencias_totales = []

        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()
                
                for numero, linea in enumerate(lineas, start=1):
                    linea_limpia = linea.strip()
                    
                    if not linea_limpia or linea_limpia.startswith("//"):
                        continue

                    # Tokenizar con regex mejorada
                    tokens = re.findall(r"\w+|==|!=|<=|>=|\+\+|--|[+\-*/=<>%(){}\[\];,]", linea_limpia)

                    # Análisis léxico
                    for token in tokens:
                        categoria = clasificar_token(token, tokens_json)
                        if categoria != "espacio" and categoria != "desconocido":
                            if token in tokens_dict:
                                tokens_dict[token]["Cantidad"] += 1
                            else:
                                tokens_dict[token] = {
                                    "Token": token,
                                    "Tipo": categoria,
                                    "Cantidad": 1
                                }
                        elif categoria == "desconocido":
                            errores_totales.append(f"❌ Línea {numero}: Token desconocido '{token}'")

                    # Análisis gramatical
                    validacion = gramatica.validar_linea(linea_limpia, numero, tokens)
                    errores_totales.extend(validacion["errores"])
                    advertencias_totales.extend(validacion["advertencias"])

        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al leer el archivo: {str(e)}")
            return

        # Mostrar resultados
        text_mensajes.tag_config("error", foreground="red", font=("Arial", 9, "bold"))
        text_mensajes.tag_config("warning", foreground="orange", font=("Arial", 9, "bold"))
        text_mensajes.tag_config("exito", foreground="green", font=("Arial", 10, "bold"))

        if errores_totales:
            for err in errores_totales:
                text_mensajes.insert(tk.END, err + "\n", "error")

        if advertencias_totales:
            for adv in advertencias_totales:
                text_mensajes.insert(tk.END, adv + "\n", "warning")

        if not errores_totales and not advertencias_totales:
            text_mensajes.insert(tk.END, "✓ Análisis exitoso sin errores\n", "exito")

        text_mensajes.insert(tk.END, f"\n📊 RESUMEN:\n", "exito")
        text_mensajes.insert(tk.END, f"   • Errores: {len(errores_totales)}\n", "error" if errores_totales else "exito")
        text_mensajes.insert(tk.END, f"   • Advertencias: {len(advertencias_totales)}\n", "warning" if advertencias_totales else "exito")
        text_mensajes.insert(tk.END, f"   • Tokens únicos: {len(tokens_dict)}\n", "exito")
        text_mensajes.insert(tk.END, f"   • Variables: {len(gramatica.variables)}\n", "exito")
        text_mensajes.insert(tk.END, f"   • Funciones: {len(gramatica.funciones)}\n", "exito")
        
        text_mensajes.config(state=tk.DISABLED)
        crear_tabla()