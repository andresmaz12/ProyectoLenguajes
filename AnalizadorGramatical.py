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
        self.estructuras_abiertas = []  # Stack para { } ( )
        self.tipos_datos = tokens_json.get("Preservada", [])
    
    def analizar_codigo(self, codigo):
        """
        Analiza un código completo
        
        Args:
            codigo (str): Código fuente completo
            
        Returns:
            dict: {
                'errores': lista de errores gramaticales,
                'advertencias': lista de advertencias,
                'variables': set de variables encontradas,
                'funciones': set de funciones encontradas
            }
        """
        self.variables = set()
        self.funciones = set()
        self.estructuras_abiertas = []
        
        errores_totales = []
        advertencias_totales = []
        
        lineas = codigo.split('\n')
        
        for numero_linea, linea in enumerate(lineas, start=1):
            linea_limpia = linea.strip()
            
            if not linea_limpia or linea_limpia.startswith("//"):
                continue
            
            tokens = self._tokenizar_linea(linea_limpia)
            validacion = self.validar_linea(linea_limpia, numero_linea, tokens)
            
            errores_totales.extend(validacion["errores"])
            advertencias_totales.extend(validacion["advertencias"])
        
        return {
            'errores': errores_totales,
            'advertencias': advertencias_totales,
            'variables': self.variables,
            'funciones': self.funciones
        }
    
    def _tokenizar_linea(self, linea):
        """Tokeniza una línea"""
        return re.findall(r"\w+|==|!=|<=|>=|\+\+|--|[+\-*/=<>%(){}\[\];,]", linea)
        
    def validar_linea(self, linea, numero_linea, tokens):
        """
        ⚠ ESTE MÉTODO SE MANTIENE IGUAL QUE EN ComprobacionDatos.py
        Valida una línea según reglas gramaticales
        """
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
        
        # Regla 3: Estructura de control (if, while, for)
        if self._es_estructura_control(tokens):
            resultado = self._validar_estructura_control(tokens, numero_linea)
            errores.extend(resultado["errores"])
            advertencias.extend(resultado["advertencias"])
        
        # Regla 4: Llamada a función
        if self._es_llamada_funcion(tokens):
            resultado = self._validar_llamada_funcion(tokens, numero_linea)
            errores.extend(resultado["errores"])
            advertencias.extend(resultado["advertencias"])
        
        # Regla 5: Paréntesis y llaves balanceadas
        errores.extend(self._validar_balanceo(tokens, numero_linea))
        
        # Regla 6: Detección de ambigüedad
        advertencias.extend(self._detectar_ambiguedad(tokens, numero_linea))
        
        return {"errores": errores, "advertencias": advertencias}
    
    # ========== MÉTODOS PRIVADOS (SE MANTIENEN IGUALES) ==========
    
    def _es_declaracion(self, tokens):
        """⚠ SE MANTIENE IGUAL - Detecta si es una declaración de variable"""
        return len(tokens) >= 2 and tokens[0] in self.tipos_datos
    
    def _validar_declaracion(self, tokens, linea):
        """⚠ SE MANTIENE IGUAL - Valida: tipo nombre [= valor];"""
        resultado = {"errores": [], "advertencias": []}
        
        if len(tokens) < 2:
            resultado["errores"].append(f"⚠ Línea {linea}: Declaración incompleta")
            return resultado
        
        # Verificar que el segundo token sea un identificador válido
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", tokens[1]):
            resultado["errores"].append(f"⚠ Línea {linea}: '{tokens[1]}' no es un identificador válido")
            return resultado
        
        self.variables.add(tokens[1])
        
        # Advertencia si no hay inicialización
        if len(tokens) == 2 or (len(tokens) == 3 and tokens[-1] == ";"):
            resultado["advertencias"].append(f"⚠️ Línea {linea}: Variable '{tokens[1]}' declarada pero no inicializada")
        
        return resultado
    
    def _contiene_asignacion(self, tokens):
        """⚠ SE MANTIENE IGUAL - Detecta si hay asignación (=) pero no es comparación (==)"""
        return "=" in tokens and "==" not in " ".join(tokens)
    
    def _validar_asignacion(self, tokens, linea):
        """⚠ SE MANTIENE IGUAL - Valida asignaciones: variable = valor;"""
        resultado = {"errores": [], "advertencias": []}
        
        if "=" not in tokens:
            return resultado
        
        idx = tokens.index("=")
        
        if idx == 0:
            resultado["errores"].append(f"⚠ Línea {linea}: Asignación sin variable")
            return resultado
        
        var = tokens[idx - 1]
        
        # Detectar ambigüedad: ¿es comparación o asignación?
        if idx + 1 < len(tokens) and tokens[idx + 1] == "=":
            # Es comparación ==, no asignación
            return resultado
        
        if var not in self.variables and not re.match(r"^\d+", var):
            resultado["errores"].append(f"⚠ Línea {linea}: Variable '{var}' no declarada antes de usar")
        
        return resultado
    
    def _es_estructura_control(self, tokens):
        """⚠ SE MANTIENE IGUAL - Detecta if, while, for"""
        return any(kw in tokens for kw in ["if", "while", "for", "else"])
    
    def _validar_estructura_control(self, tokens, linea):
        """⚠ SE MANTIENE IGUAL - Valida: if/while/for (condición) { ... }"""
        resultado = {"errores": [], "advertencias": []}
        
        ctrl_keywords = ["if", "while", "for"]
        keyword = None
        
        for kw in ctrl_keywords:
            if kw in tokens:
                keyword = kw
                break
        
        if not keyword:
            return resultado
        
        idx = tokens.index(keyword)
        
        # Verificar que exista paréntesis después
        if idx + 1 >= len(tokens) or tokens[idx + 1] != "(":
            resultado["errores"].append(f"⚠ Línea {linea}: '{keyword}' debe ir seguido de '('")
            return resultado
        
        # Para 'for', verificar estructura: for (init; cond; inc)
        if keyword == "for":
            if ";" not in tokens:
                resultado["errores"].append(f"⚠ Línea {linea}: 'for' requiere formato: for(init; condición; incremento)")
            else:
                semicolons = [i for i, t in enumerate(tokens) if t == ";"]
                if len(semicolons) != 2:
                    resultado["advertencias"].append(f"⚠️ Línea {linea}: Estructura 'for' incompleta (se esperan 2 ';')")
        
        return resultado
    
    def _es_llamada_funcion(self, tokens):
        """⚠ SE MANTIENE IGUAL - Detecta llamadas a función: nombre()"""
        for i, token in enumerate(tokens):
            if i + 1 < len(tokens) and tokens[i + 1] == "(":
                if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", token):
                    return True
        return False
    
    def _validar_llamada_funcion(self, tokens, linea):
        """⚠ SE MANTIENE IGUAL - Valida llamadas a función"""
        resultado = {"errores": [], "advertencias": []}
        
        for i, token in enumerate(tokens):
            if i + 1 < len(tokens) and tokens[i + 1] == "(":
                if token not in ["if", "while", "for"] and token not in self.funciones:
                    self.funciones.add(token)
        
        return resultado
    
    def _validar_balanceo(self, tokens, linea):
        """⚠ SE MANTIENE IGUAL - Valida que paréntesis y llaves estén balanceados"""
        errores = []
        pares = {"(": ")", "{": "}", "[": "]"}
        stack = []
        
        for i, token in enumerate(tokens):
            if token in pares:
                stack.append((token, linea, i))
            elif token in pares.values():
                if not stack:
                    errores.append(f"⚠ Línea {linea}: '{token}' sin apertura")
                elif pares[stack[-1][0]] != token:
                    errores.append(f"⚠ Línea {linea}: No coinciden '{stack[-1][0]}' con '{token}'")
                else:
                    stack.pop()
        
        for token, line, pos in stack:
            errores.append(f"⚠ Línea {line}: '{token}' no cerrado")
        
        return errores
    
    def _detectar_ambiguedad(self, tokens, linea):
        """⚠ SE MANTIENE IGUAL - Detecta construcciones ambiguas o potencialmente problemáticas"""
        advertencias = []
        
        # Ambigüedad 1: Operadores sin espacios
        linea_str = " ".join(tokens)
        if re.search(r"\w[+\-*/%]\w", linea_str):
            advertencias.append(f"⚠️ Línea {linea}: Operador sin espacios (ambigüedad)")
        
        # Ambigüedad 2: Asignación dentro de condición
        if "if" in tokens or "while" in tokens:
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