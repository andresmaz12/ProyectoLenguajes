import re

class AnalizadorGramatical:
    """Validador de reglas gramaticales y sintaxis"""
    
    def __init__(self, tokens_json):
        """
        Inicializa el analizador gramatical
        
        Args:
            tokens_json (dict): Diccionario con categorías de tokens
        """
        self.tokens_json = tokens_json
        self.variables = set()
        self.funciones = set()
        self.estructuras_abiertas = []  # Stack para 'si', 'mientras', 'func'
    
    def analizar_codigo(self, codigo):
        """
        Analiza el código fuente completo y devuelve los resultados gramaticales
        """
        errores = []
        advertencias = []

        # Limpieza básica
        lineas = codigo.split('\n')
        
        for num_linea, linea in enumerate(lineas, start=1):
            linea = linea.strip()
            if not linea or linea.startswith("//"):
                continue

            # --- Declaración de variables ---
            match_var = re.match(r'^(entero|decimal|cadena|booleano|caracter)\s+([a-zA-Z_]\w*)\s*=\s*(.+);$', linea)
            if match_var:
                tipo, nombre, valor = match_var.groups()
                if nombre in self.variables:
                    advertencias.append(f"⚠️ Línea {num_linea}: Variable '{nombre}' redeclarada")
                else:
                    self.variables.add(nombre)
                continue

            # --- Declaración de funciones ---
            match_func = re.match(r'^func\s+([a-zA-Z_]\w*)\s*\(([^)]*)\)\s*siguiente$', linea)
            if match_func:
                nombre_func = match_func.group(1)
                if nombre_func in self.funciones:
                    advertencias.append(f"⚠️ Línea {num_linea}: Función '{nombre_func}' redeclarada")
                else:
                    self.funciones.add(nombre_func)
                self.estructuras_abiertas.append('func')
                continue

            # --- Estructura de control SI ---
            match_si = re.match(r'^si\s*\(([^)]*)\)\s*siguiente$', linea)
            if match_si:
                self.estructuras_abiertas.append('si')
                continue

            # --- Estructura de control SINO ---
            if re.match(r'^finaliza\s*sino\s*siguiente$', linea):
                if not self.estructuras_abiertas or self.estructuras_abiertas[-1] != 'si':
                    errores.append(f"⚠ Línea {num_linea}: 'sino' sin un 'si' previo")
                continue

            # --- Estructura MIENTRAS ---
            if re.match(r'^mientras\s*\(([^)]*)\)\s*siguiente$', linea):
                self.estructuras_abiertas.append('mientras')
                continue

            # --- Finaliza bloque ---
            if re.match(r'^finaliza$', linea):
                if not self.estructuras_abiertas:
                    errores.append(f"⚠ Línea {num_linea}: 'finaliza' sin bloque abierto")
                else:
                    self.estructuras_abiertas.pop()
                continue

            # --- Llamada a función ---
            if re.match(r'^[a-zA-Z_]\w*\s*\(.*\);$', linea):
                continue

            # --- Operaciones matemáticas ---
            if re.match(r'^[a-zA-Z_]\w*\s*=\s*.+;$', linea):
                continue

            # --- Arrays ---
            if re.match(r'^[a-zA-Z_]\w*\[\d+\]\s*=\s*.+;$', linea):
                continue

            # Si no coincide con ninguna regla
            errores.append(f"⚠ Línea {num_linea}: Sintaxis no válida -> {linea}")

        # --- Validar estructuras abiertas al final ---
        for estructura in self.estructuras_abiertas:
            errores.append(f"⚠ Bloque '{estructura}' no cerrado con 'finaliza'")

        # Retornar resultados en el formato que usa tu interfaz
        return {
            'errores': errores,
            'advertencias': advertencias,
            'variables': list(self.variables),
            'funciones': list(self.funciones)
        }
