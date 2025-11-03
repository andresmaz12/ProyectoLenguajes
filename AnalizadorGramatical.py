import re

class AnalizadorGramatical:
    """Validador de reglas gramaticales y sintaxis"""
    
    def __init__(self, tokens_json):
        self.tokens_json = tokens_json
        self.variables = {}
        self.funciones = set()
        self.estructuras_abiertas = []
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
                'variables': dict de variables encontradas,
                'funciones': set de funciones encontradas
            }
        """
        self.variables = {}
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
        
        # Validar que todas las estructuras estén cerradas
        if self.estructuras_abiertas:
            for estructura in self.estructuras_abiertas:
                errores_totales.append(
                    f"⚠ Línea {estructura['linea']}: '{estructura['tipo']}' sin 'finaliza'"
                )
        
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
        
    def validar_linea(self, linea, numero_linea, tokens):
        errores = []
        advertencias = []
        
        # Detectar 'siguiente' y 'finaliza'
        if "siguiente" in tokens:
            resultado = self._validar_siguiente(tokens, numero_linea)
            errores.extend(resultado["errores"])
            advertencias.extend(resultado["advertencias"])
        
        if "finaliza" in tokens:
            resultado = self._validar_finaliza(tokens, numero_linea)
            errores.extend(resultado["errores"])
            advertencias.extend(resultado["advertencias"])
        
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
        
        # Regla 5: Paréntesis y corchetes balanceados (ya no llaves)
        errores.extend(self._validar_balanceo(tokens, numero_linea))
        
        # Regla 6: Detección de ambigüedad
        advertencias.extend(self._detectar_ambiguedad(tokens, numero_linea))

        # Regla 7: Declaración de funciones
        if self._es_declaracion_funcion(tokens):
            resultado = self._validar_declaracion_funcion(tokens, numero_linea)
            errores.extend(resultado["errores"])
            advertencias.extend(resultado["advertencias"])

        return {"errores": errores, "advertencias": advertencias}
    
    def _validar_siguiente(self, tokens, linea):
        """Valida el uso de 'siguiente'"""
        resultado = {"errores": [], "advertencias": []}
        
        # 'siguiente' debe aparecer después de una estructura de control o función
        if not self.estructuras_abiertas:
            resultado["errores"].append(
                f"⚠ Línea {linea}: 'siguiente' sin estructura previa (si/mientras/para/func)"
            )
        
        return resultado
    
    def _validar_finaliza(self, tokens, linea):
        """Valida el uso de 'finaliza'"""
        resultado = {"errores": [], "advertencias": []}
        
        if not self.estructuras_abiertas:
            resultado["errores"].append(
                f"⚠ Línea {linea}: 'finaliza' sin estructura abierta"
            )
        else:
            # Cerrar la última estructura abierta
            self.estructuras_abiertas.pop()
        
        return resultado
    
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
    
    def _es_estructura_control(self, tokens):
        """Detecta if, while, for"""
        return any(kw in tokens for kw in ["si", "mientras", "para", "sino"])
    
    def _validar_estructura_control(self, tokens, linea):
        """Valida: if/while/for (condición) siguiente ... finaliza"""
        resultado = {"errores": [], "advertencias": []}
        
        ctrl_keywords = ["si", "mientras", "para"]
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
        
        # Verificar que termine con 'siguiente'
        if "siguiente" not in tokens:
            resultado["advertencias"].append(
                f"⚠️ Línea {linea}: '{keyword}' debería terminar con 'siguiente'"
            )
        else:
            # Registrar estructura abierta
            self.estructuras_abiertas.append({
                'tipo': keyword,
                'linea': linea
            })
        
        # Para 'para', verificar estructura: para (init; cond; inc)
        if keyword == "para":
            if ";" not in tokens:
                resultado["errores"].append(
                    f"⚠ Línea {linea}: 'para' requiere formato: para(init; condición; incremento)"
                )
            else:
                semicolons = [i for i, t in enumerate(tokens) if t == ";"]
                if len(semicolons) != 2:
                    resultado["advertencias"].append(
                        f"⚠️ Línea {linea}: Estructura 'para' incompleta (se esperan 2 ';')"
                    )
        
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
                if token not in ["si", "mientras", "para"] and token not in self.funciones:
                    self.funciones.add(token)
        
        return resultado
    
    def _validar_balanceo(self, tokens, linea):
        """Valida que paréntesis y corchetes estén balanceados (ya no llaves)"""
        errores = []
        pares = {"(": ")", "[": "]"}
        stack = []

        for i, token in enumerate(tokens):
            # Ignorar saltos de línea y palabras clave que no son delimitadores
            if token == "\n" or token in ["siguiente", "finaliza", "sino"]:
                continue

            if token in pares:
                stack.append((token, linea, i))
            elif token in pares.values():
                if not stack:
                    errores.append(f"⚠ Línea {linea}: '{token}' sin apertura")
                elif pares[stack[-1][0]] != token:
                    errores.append(f"⚠ Línea {linea}: No coinciden '{stack[-1][0]}' con '{token}'")
                else:
                    stack.pop()

        # Solo reportar error si hay paréntesis/corchetes sin cerrar AL FINAL DE LA LÍNEA
        for token, line, pos in stack:
            errores.append(f"⚠ Línea {line}: '{token}' no cerrado")

        return errores

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
        
        # Verificar que termine con 'siguiente'
        if "siguiente" not in tokens:
            resultado["advertencias"].append(
                f"⚠️ Línea {linea}: La función debería terminar con 'siguiente'"
            )
        else:
            # Registrar estructura abierta
            self.estructuras_abiertas.append({
                'tipo': 'func',
                'linea': linea
            })
        
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