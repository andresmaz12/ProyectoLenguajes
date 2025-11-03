import re
import json

class AnalizadorLexico:
    def __init__(self, ruta_tokens_json="Tokens.json"):
        """Inicializa el analizador léxico con las categorías de tokens"""
        self.tokens_json = self._cargar_tokens_json(ruta_tokens_json)
        self.tokens_dict = {}  # Almacena tokens encontrados {token: {Token, Tipo, Cantidad}}
    
    def _cargar_tokens_json(self, ruta):
        """Carga el archivo JSON de tokens"""
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                tokens = json.load(archivo)
            print("✓ JSON de tokens cargado correctamente")
            return tokens
        except FileNotFoundError:
            print("⚠ No se encontró Tokens.json, creando uno por defecto...")
            tokens = {
                "Preservada": ["entero", "decimal", "caracter", "si", "sino", "mientras", "para", "imprimir","func"],
                "operadores": ["+", "-", "*", "/", "=", "==", "!=", "<=", ">=", "<", ">", "%", "++", "--"],
                "signos": ["(", ")", "{", "}", ";", ",", "[", "]"]
            }
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(tokens, f, indent=4, ensure_ascii=False)
            return tokens
        except json.JSONDecodeError:
            raise ValueError("⚠ El archivo Tokens.json tiene formato inválido")
    
    def clasificar_token(self, token):
        if re.match(r'^".*"$', token):
            return "cadena"

        if token in self.tokens_json.get("Preservada", []):
            return "Preservada"
        if token in self.tokens_json.get("operadores", []):
            return "operadores"
        if token in self.tokens_json.get("signos", []):
            return "signos"
        if re.match(r"^\d+(\.\d+)?$", token):
            return "numeros"
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", token):
            return "identificadores"
        if token == " ":
            return "espacio"
        if token == "\n":
            return "salto de linea"
        return "desconocido"

    def tokenizar_linea(self, linea):
    # Mejor patrón para cadenas con escapes
        patron = r'"(?:\\.|[^"\\])*"|\w+|==|!=|<=|>=|\+\+|--|[+\-*/=<>%(){}\[\];,]|\n'
        return re.findall(patron, linea)

    def registrar_token(self, token):
        """
        Registra un token en el diccionario interno
        
        Args:
            token (str): Token a registrar
            categoria (str): Categoría del token
        """
        categoria = self.clasificar_token(token)
        
        if categoria not in ["espacio", "desconocido"]:
            if token in self.tokens_dict:
                self.tokens_dict[token]["Cantidad"] += 1
            else:
                self.tokens_dict[token] = {
                    "Token": token,
                    "Tipo": categoria,
                    "Cantidad": 1
                }
    
    def analizar_codigo(self, codigo):
        """
        Analiza un código completo línea por línea
        
        Args:
            codigo (str): Código fuente completo
            
        Returns:
            dict: {
                'tokens': dict con tokens encontrados,
                'errores_lexicos': lista de errores léxicos encontrados
            }
        """
        self.tokens_dict = {}  # Reiniciar contador
        errores_lexicos = []
        
        lineas = codigo.split('\n')
        
        for numero_linea, linea in enumerate(lineas, start=1):
            # Eliminar comentarios inline
            if '//' in linea:
                linea = linea[:linea.index('//')]
            
            linea_limpia = linea.strip()
            
            # Ignorar líneas vacías
            if not linea_limpia:
                continue
            
            tokens = self.tokenizar_linea(linea_limpia)
            
            for token in tokens:
                categoria = self.clasificar_token(token)
                
                if categoria == "desconocido":
                    errores_lexicos.append({
                        'linea': numero_linea,
                        'token': token,
                        'mensaje': f"⚠ Línea {numero_linea}: Token desconocido '{token}'"
                    })
                else:
                    self.registrar_token(token)
        
        return {
            'tokens': self.tokens_dict,
            'errores_lexicos': errores_lexicos
        }
    
    def obtener_tokens_ordenados(self):
        """
        Obtiene los tokens ordenados por tipo y nombre
        
        Returns:
            list: Lista de tuplas (token, datos) ordenadas
        """
        return sorted(self.tokens_dict.items(), key=lambda x: (x[1]["Tipo"], x[0]))
    
    def get_tokens_json(self):
        """Retorna el diccionario de tokens JSON cargado"""
        return self.tokens_json