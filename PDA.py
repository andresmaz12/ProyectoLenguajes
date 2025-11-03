class PDA:
    """
    Autómata de Pila (Pushdown Automaton) para validar la sintaxis del lenguaje
    """
    
    def __init__(self):
        self.pila = []
        self.estado = "q0"  # Estado inicial
        self.errores = []
        self.advertencias = []
        
        # Mapeo de símbolos de apertura y cierre
        self.pares = {
            "(": ")",
            "[": "]",
            "si": "finaliza",
            "mientras": "finaliza",
            "para": "finaliza",
            "func": "finaliza",
            "sino": "finaliza"
        }
        
        # Símbolos que requieren 'siguiente' antes de su contenido
        self.requiere_siguiente = ["si", "mientras", "para", "func", "sino"]
        
    def reiniciar(self):
        """Reinicia el PDA para un nuevo análisis"""
        self.pila = []
        self.estado = "q0"
        self.errores = []
        self.advertencias = []
    
    def procesar_token(self, token, linea):
        """
        Procesa un token según las reglas del PDA
        
        Args:
            token: Token a procesar
            linea: Número de línea actual
        """
        # Transición 1: Detectar apertura de estructuras
        if token in ["si", "mientras", "para", "func"]:
            self.pila.append({
                'simbolo': token,
                'linea': linea,
                'tiene_siguiente': False,
                'espera_parentesis': True
            })
            self.estado = "esperando_parentesis"
        
        # Transición 2: Validar paréntesis de apertura
        elif token == "(" and self.estado == "esperando_parentesis":
            if self.pila:
                self.pila.append({
                    'simbolo': '(',
                    'linea': linea,
                    'tipo': 'parentesis'
                })
            else:
                # Paréntesis en expresión normal
                self.pila.append({
                    'simbolo': '(',
                    'linea': linea,
                    'tipo': 'parentesis'
                })
            self.estado = "dentro_parentesis"
        
        # Transición 3: Paréntesis de apertura general
        elif token == "(":
            self.pila.append({
                'simbolo': '(',
                'linea': linea,
                'tipo': 'parentesis'
            })
        
        # Transición 4: Paréntesis de cierre
        elif token == ")":
            if not self.pila:
                self.errores.append(f"⚠ Línea {linea}: ')' sin '(' correspondiente")
            else:
                # Buscar el último '(' en la pila
                encontrado = False
                temp_stack = []
                
                while self.pila:
                    top = self.pila.pop()
                    if top['simbolo'] == '(':
                        encontrado = True
                        # Restaurar elementos que no eran paréntesis
                        while temp_stack:
                            self.pila.append(temp_stack.pop())
                        break
                    else:
                        temp_stack.append(top)
                
                if not encontrado:
                    self.errores.append(f"⚠ Línea {linea}: ')' sin '(' correspondiente")
                    # Restaurar la pila
                    while temp_stack:
                        self.pila.append(temp_stack.pop())
                
                # Cambiar estado después del paréntesis de cierre
                if self.estado == "dentro_parentesis":
                    self.estado = "esperando_siguiente"
        
        # Transición 5: Detectar 'siguiente'
        elif token == "siguiente":
            if self.pila:
                # Buscar la última estructura de control en la pila
                for i in range(len(self.pila) - 1, -1, -1):
                    if self.pila[i]['simbolo'] in self.requiere_siguiente:
                        self.pila[i]['tiene_siguiente'] = True
                        break
            self.estado = "dentro_bloque"
        
        # Transición 6: Detectar 'sino'
        elif token == "sino":
            # Validar que exista un 'si' previo cerrado
            self.pila.append({
                'simbolo': 'sino',
                'linea': linea,
                'tiene_siguiente': False,
                'espera_parentesis': False
            })
            self.estado = "esperando_siguiente"
        
        # Transición 7: Corchetes de apertura
        elif token == "[":
            self.pila.append({
                'simbolo': '[',
                'linea': linea,
                'tipo': 'corchete'
            })
        
        # Transición 8: Corchetes de cierre
        elif token == "]":
            if not self.pila or self.pila[-1]['simbolo'] != '[':
                self.errores.append(f"⚠ Línea {linea}: ']' sin '[' correspondiente")
            else:
                self.pila.pop()
        
        # Transición 9: Detectar 'finaliza'
        elif token == "finaliza":
            if not self.pila:
                self.errores.append(f"⚠ Línea {linea}: 'finaliza' sin estructura que cerrar")
            else:
                # Buscar la última estructura que requiere finaliza
                encontrado = False
                
                for i in range(len(self.pila) - 1, -1, -1):
                    elem = self.pila[i]
                    if elem['simbolo'] in self.requiere_siguiente:
                        # Validar que tenga 'siguiente'
                        if not elem.get('tiene_siguiente', False):
                            self.advertencias.append(
                                f"⚠️ Línea {elem['linea']}: '{elem['simbolo']}' cerrado con 'finaliza' pero sin 'siguiente'"
                            )
                        self.pila.pop(i)
                        encontrado = True
                        break
                
                if not encontrado:
                    self.errores.append(f"⚠ Línea {linea}: 'finaliza' sin estructura correspondiente")
            
            self.estado = "q0"
    
    def procesar_linea(self, tokens, numero_linea):
        """
        Procesa una línea completa de tokens
        
        Args:
            tokens: Lista de tokens de la línea
            numero_linea: Número de línea
        """
        for token in tokens:
            if token not in [" ", "\n", ""]:
                self.procesar_token(token, numero_linea)
    
    def validar_final(self):
        """
        Valida que la pila esté vacía al final del análisis
        """
        if self.pila:
            for elem in self.pila:
                simbolo = elem['simbolo']
                linea = elem['linea']
                
                if simbolo in self.requiere_siguiente:
                    self.errores.append(
                        f"⚠ Línea {linea}: '{simbolo}' sin 'finaliza' correspondiente"
                    )
                elif simbolo == '(':
                    self.errores.append(
                        f"⚠ Línea {linea}: '(' sin ')' correspondiente"
                    )
                elif simbolo == '[':
                    self.errores.append(
                        f"⚠ Línea {linea}: '[' sin ']' correspondiente"
                    )
    
    def obtener_resultados(self):
        """
        Retorna los errores y advertencias acumulados
        
        Returns:
            dict: {'errores': [], 'advertencias': []}
        """
        return {
            'errores': self.errores.copy(),
            'advertencias': self.advertencias.copy()
        }
    
    def obtener_estado_pila(self):
        """
        Retorna el estado actual de la pila (útil para debugging)
        
        Returns:
            list: Copia de la pila actual
        """
        return self.pila.copy()