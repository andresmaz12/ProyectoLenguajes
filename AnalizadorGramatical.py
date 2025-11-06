import re
from PDA import PDA

class AnalizadorGramatical:
    """Validador de reglas gramaticales y sintaxis usando PDA"""
    
    def __init__(self, tokens_json):
        self.tokens_json = tokens_json
        self.variables = {}
        self.funciones = set()
        self.tipos_datos = tokens_json.get("Preservada", [])
        self.pda = PDA()  # Instancia del Autómata de Pila
        
    def analizar_codigo(self, codigo):
        """
        Analiza un código completo usando PDA y validaciones semánticas
        
        Args:
            codigo (str): Código fuente completo
            
        Returns:
            dict: {
                'errores': lista de errores gramaticales,
                'advertencias': lista de advertencias,
                'variables': dict de variables encontradas,
                'funciones': set de funciones encontradas
            }
        """
        self.variables = {}
        self.funciones = set()
        self.pda.reiniciar()
        
        errores_totales = []
        advertencias_totales = []
        
        lineas = codigo.split('\n')
        
        # Primera pasada: Análisis con PDA
        for numero_linea, linea in enumerate(lineas, start=1):
            linea_limpia = linea.strip()
            
            if not linea_limpia or linea_limpia.startswith("//"):
                continue
            
            tokens = self._tokenizar_linea(linea_limpia)
            
            # Procesar con PDA
            self.pda.procesar_linea(tokens, numero_linea)
            
            # Validaciones semánticas adicionales
            validacion = self.validar_semantica(linea_limpia, numero_linea, tokens)
            errores_totales.extend(validacion["errores"])
            advertencias_totales.extend(validacion["advertencias"])
        
        # Validar que el PDA termine en estado válido
        self.pda.validar_final()
        
        # Obtener resultados del PDA
        resultados_pda = self.pda.obtener_resultados()
        errores_totales.extend(resultados_pda['errores'])
        advertencias_totales.extend(resultados_pda['advertencias'])
        
        return {
            'errores': errores_totales,
            'advertencias': advertencias_totales,
            'variables': self.variables,
            'funciones': self.funciones
        }
    
    def _tokenizar_linea(self, linea):
        """Tokeniza una línea"""
        patron = r'"(?:\\.|[^"\\])*"|\w+|==|!=|<=|>=|\+\+|--|[+\-*/=<>%(){}\[\];,]|\n'
        tokens = re.findall(patron, linea)
        tokens_limpios = [t for t in tokens if t not in ('"', "''") and t.strip() != '']
        return tokens_limpios
        
    def validar_semantica(self, linea, numero_linea, tokens):
        """Validaciones semánticas (declaraciones, tipos, etc.)"""
        errores = []
        advertencias = []
        
        # Regla 1: Declaración de variables
        if self._es_declaracion(tokens):
            resultado = self._validar_declaracion(tokens, numero_linea)
            errores.extend(resultado["errores"])
            advertencias.extend(resultado["advertencias"])
        
        # Regla 2: Asignación de valores
        if self._contiene_asignacion(tokens):
            resultado = self._validar_asignacion(tokens, numero_linea)
            errores.extend(resultado["errores"])
            advertencias.extend(resultado["advertencias"])
        
        # Regla 3: Llamada a función
        if self._es_llamada_funcion(tokens):
            resultado = self._validar_llamada_funcion(tokens, numero_linea)
            errores.extend(resultado["errores"])
            advertencias.extend(resultado["advertencias"])
        
        # Regla 4: Declaración de funciones
        if self._es_declaracion_funcion(tokens):
            resultado = self._validar_declaracion_funcion(tokens, numero_linea)
            errores.extend(resultado["errores"])
            advertencias.extend(resultado["advertencias"])
        
        # Regla 5: Detección de ambigüedad
        advertencias.extend(self._detectar_ambiguedad(tokens, numero_linea))

        return {"errores": errores, "advertencias": advertencias}
    
    def _es_declaracion(self, tokens):
        """Detecta si es una declaración de variable"""
        return len(tokens) >= 2 and tokens[0] in self.tipos_datos
    
    def _validar_declaracion(self, tokens, linea):
        """Valida una declaración: tipo nombre [= valor];"""
        resultado = {"errores": [], "advertencias": []}

        if len(tokens) < 2:
            resultado["errores"].append(f"⚠ Línea {linea}: Declaración incompleta")
            return resultado

        tipo_dato = tokens[0]
        nombre_var = tokens[1]

        # Verificar identificador válido
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", nombre_var):
            resultado["errores"].append(f"⚠ Línea {linea}: '{nombre_var}' no es un identificador válido")
            return resultado

        # Registrar variable
        self.variables[nombre_var] = tipo_dato

        # Sin inicialización
        if len(tokens) == 2 or (len(tokens) == 3 and tokens[-1] == ";"):
            resultado["advertencias"].append(f"⚠️ Línea {linea}: Variable '{nombre_var}' declarada pero no inicializada")
            return resultado

        # Si tiene asignación
        if "=" in tokens:
            idx = tokens.index("=")
            if idx + 1 >= len(tokens):
                resultado["errores"].append(f"⚠ Línea {linea}: Falta valor en la asignación")
                return resultado

            valor = tokens[idx + 1]

            # Validación según tipo
            if tipo_dato == "cadena":
                if not re.match(r'^".*"$', valor):
                    resultado["errores"].append(
                        f"⚠ Línea {linea}: Las variables tipo 'cadena' deben tener valores entre comillas dobles (\"texto\")"
                    )

            elif tipo_dato == "booleano":
                if valor not in ["verdadero", "falso"]:
                    resultado["errores"].append(
                        f"⚠ Línea {linea}: Las variables tipo 'booleano' solo pueden ser 'verdadero' o 'falso'"
                    )

            elif tipo_dato == "entero":
                if not re.match(r"^\d+$", valor):
                    resultado["errores"].append(
                        f"⚠ Línea {linea}: Valor '{valor}' inválido para tipo 'entero'"
                    )

            elif tipo_dato == "decimal":
                if not re.match(r"^\d+(\.\d+)?$", valor):
                    resultado["errores"].append(
                        f"⚠ Línea {linea}: Valor '{valor}' inválido para tipo 'decimal'"
                    )

        return resultado
    
    def _contiene_asignacion(self, tokens):
        """Detecta si hay asignación (=) pero no es comparación (==)"""
        return "=" in tokens and "==" not in " ".join(tokens)
    
    def _validar_asignacion(self, tokens, linea):
        resultado = {"errores": [], "advertencias": []}
        
        if "=" not in tokens:
            return resultado
        
        idx = tokens.index("=")
        
        if idx == 0:
            resultado["errores"].append(f"⚠ Línea {linea}: Asignación sin variable")
            return resultado
        
        var = tokens[idx - 1]
        
        # Detectar si es comparación ==
        if idx + 1 < len(tokens) and tokens[idx + 1] == "=":
            return resultado
        
        # Validar que la variable esté declarada
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var):
            if var not in self.variables:
                resultado["errores"].append(f"⚠ Línea {linea}: Variable '{var}' no declarada")
                return resultado
        
            # Validar tipo de dato
            if idx + 1 < len(tokens):
                valor = tokens[idx + 1]
                tipo_var = self.variables[var]
                
                if tipo_var == "entero" and not re.match(r"^\d+$", valor):
                    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", valor):
                        resultado["errores"].append(f"⚠ Línea {linea}: Tipo incompatible, '{var}' es 'entero'")
                
                elif tipo_var == "cadena" and not re.match(r'^".*"$', valor):
                    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", valor):
                        resultado["errores"].append(f"⚠ Línea {linea}: Tipo incompatible, '{var}' es 'cadena'")
                
                elif tipo_var == "booleano" and valor not in ["verdadero", "falso"]:
                    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", valor):
                        resultado["errores"].append(f"⚠ Línea {linea}: Tipo incompatible, '{var}' es 'booleano'")
            
        return resultado
    
    def _es_llamada_funcion(self, tokens):
        """Detecta llamadas a función: nombre()"""
        for i, token in enumerate(tokens):
            if i + 1 < len(tokens) and tokens[i + 1] == "(":
                if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", token):
                    return True
        return False
    
    def _validar_llamada_funcion(self, tokens, linea):
        """Valida llamadas a función"""
        resultado = {"errores": [], "advertencias": []}
        
        for i, token in enumerate(tokens):
            if i + 1 < len(tokens) and tokens[i + 1] == "(":
                if token not in ["si", "mientras", "para", "imprimir"] and token not in self.funciones:
                    self.funciones.add(token)
        
        return resultado
    
    def _es_declaracion_funcion(self, tokens):
        """Detecta declaración de función: func nombre() siguiente ... finaliza"""
        return "func" in tokens

    def _validar_declaracion_funcion(self, tokens, linea):
        """Valida declaración de funciones"""
        resultado = {"errores": [], "advertencias": []}
        
        if "func" not in tokens:
            return resultado
        
        idx = tokens.index("func")
    
        # Verificar que haya nombre después de func
        if idx + 1 >= len(tokens):
            resultado["errores"].append(f"⚠ Línea {linea}: 'func' debe ir seguido del nombre de la función")
            return resultado
        
        nombre_func = tokens[idx + 1]
        
        # Verificar identificador válido
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", nombre_func):
            resultado["errores"].append(f"⚠ Línea {linea}: '{nombre_func}' no es un nombre de función válido")
            return resultado
        
        # Registrar función
        if nombre_func in self.funciones:
            resultado["advertencias"].append(f"⚠️ Línea {linea}: Función '{nombre_func}' redeclarada")
        else:
            self.funciones.add(nombre_func)
        
        # Verificar paréntesis
        if idx + 2 >= len(tokens) or tokens[idx + 2] != "(":
            resultado["errores"].append(f"⚠ Línea {linea}: Falta '(' después del nombre de la función")
        
        return resultado

    def _detectar_ambiguedad(self, tokens, linea):
        """Detecta construcciones ambiguas o potencialmente problemáticas"""
        advertencias = []
        
        # Ambigüedad 1: Operadores sin espacios
        linea_str = " ".join(tokens)
        if re.search(r"\w[+\-*/%]\w", linea_str):
            advertencias.append(f"⚠️ Línea {linea}: Operador sin espacios (ambigüedad)")
        
        # Ambigüedad 2: Asignación dentro de condición
        if "si" in tokens or "mientras" in tokens:
            if "=" in tokens and "==" not in " ".join(tokens):
                advertencias.append(f"⚠️ Línea {linea}: ¿Asignación dentro de condición? (ambigüedad)")
        
        # Ambigüedad 3: Operadores consecutivos
        for i in range(len(tokens) - 1):
            if tokens[i] in ["+", "-", "*", "/", "%"] and tokens[i + 1] in ["+", "-", "*", "/", "%"]:
                advertencias.append(f"⚠️ Línea {linea}: Operadores consecutivos (ambigüedad)")
        
        # Ambigüedad 4: Múltiples asignaciones
        if tokens.count("=") > 1 and "==" not in " ".join(tokens):
            advertencias.append(f"⚠️ Línea {linea}: Asignaciones múltiples (ambigüedad)")
        
        return advertencias