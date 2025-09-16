import re
import json
import os
import sys
from pathlib import Path

class AnalizadorLexico:
    def __init__(self, ruta_json="Tokens.json"):
        self.tokenss = {}  # Diccionario para almacenar tokens encontrados
        self.categorias = self.cargar_tokens(ruta_json)
    
    def cargar_tokens(self, ruta_json):
        try:
            # Buscar el archivo en varias ubicaciones posibles
            posibles_rutas = [
                ruta_json,
                os.path.join(os.path.dirname(__file__), ruta_json),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), ruta_json)
            ]
            
            ruta_encontrada = None
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    ruta_encontrada = ruta
                    break
            
            if not ruta_encontrada:
                raise FileNotFoundError(f"No se encontró el archivo {ruta_json} en ninguna ubicación posible")
            
            with open(ruta_encontrada, "r", encoding="utf-8") as archivo:
                tokens_json = json.load(archivo)
            
            print("✓ JSON de tokens cargado correctamente")
            return tokens_json
            
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            print("Por favor, asegúrate de que el archivo Tokens.json esté en el mismo directorio que este script.")
            sys.exit(1)
        except json.JSONDecodeError:
            print("❌ Error: El archivo Tokens.json tiene formato inválido")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error inesperado al cargar el JSON: {e}")
            sys.exit(1)

    def clasificar_token(self, token):
        if token in self.categorias["Preservada"]:
            return "Preservada"
        if token in self.categorias["operadores"]:
            return "operadores"
        if token in self.categorias["signos"]:
            return "signos"
        if token in self.categorias["numeros"]:
            return "numeros"
        if token.isidentifier() and not token[0].isdigit():
            return "identificadores"
        if re.match(r"^\d+\.\d+$|^\d+$", token):
            return "numeros"
        if token.isspace() or token == "":
            return "espacio"
        
        return "desconocido"

    def analizar_archivo(self, ruta_txt):
        if not os.path.exists(ruta_txt):
            print(f"❌ Error: El archivo {ruta_txt} no existe")
            return False
        
        file_size = os.path.getsize(ruta_txt)
        print(f"✓ Tamaño del archivo: {file_size} bytes")
        
        if file_size == 0:
            print("❌ El archivo está vacío")
            return False
        
        print("-" * 50)
        
        try:
            with open(ruta_txt, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()
                print(f"✓ Número de líneas en el archivo: {len(lineas)}")
                
                for numero, linea in enumerate(lineas, start=1):
                    linea = linea.strip()
                
                    if not linea:
                        print(f"Línea {numero}: [vacía] - saltando")
                        continue

                    print(f"\nLínea {numero}: '{linea}'")
                    # Patrón regex mejorado para capturar tokens
                    tokens = re.findall(r"==|!=|<=|>=|[A-Za-z_]\w*|\d+\.\d+|\d+|[+\-*/=(){}[\];:,]|\".*?\"|'.*?'|\S+", linea)
                    
                    if not tokens:
                        print(f"  No se encontraron tokens en la línea {numero}")
                        continue
                        
                    for token in tokens:
                        categoria = self.clasificar_token(token)
                        if categoria == "desconocido":
                            print(f"  '{token}' → ¡ATENCIÓN! Token desconocido")
                        elif categoria == "espacio":
                            continue
                        else:
                            if token in self.tokenss:
                                self.tokenss[token]["Cantidad"] += 1
                            else:
                                self.tokenss[token] = {"Token": token, "Tipo": categoria, "Cantidad": 1}
                            print(f"  '{token}' → Tipo: {categoria}, Cantidad actual: {self.tokenss[token]['Cantidad']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al procesar el archivo: {e}")
            return False

    def mostrar_estadisticas(self):
        if not self.tokenss:
            print("No se encontraron tokens para mostrar estadísticas.")
            return
        
        print("\n" + "="*50)
        print("ESTADÍSTICAS DE TOKENS")
        print("="*50)
        
        # Contadores por tipo
        contadores = {}
        for token_info in self.tokenss.values():
            tipo = token_info["Tipo"]
            if tipo in contadores:
                contadores[tipo] += token_info["Cantidad"]
            else:
                contadores[tipo] = token_info["Cantidad"]
        
        # Mostrar estadísticas por tipo
        for tipo, cantidad in contadores.items():
            print(f"{tipo}: {cantidad} tokens")
        
        print(f"\nTotal de tokens únicos: {len(self.tokenss)}")
        print(f"Total de todos los tokens: {sum(contadores.values())}")

    def guardar_resultados(self, ruta_salida="resultados_analisis.json"):
        try:
            with open(ruta_salida, "w", encoding="utf-8") as archivo:
                # Preparar datos para exportación
                datos_exportacion = {
                    "tokens": list(self.tokenss.values()),
                    "resumen": {
                        "total_tokens_unicos": len(self.tokenss),
                        "total_todos_tokens": sum(info["Cantidad"] for info in self.tokenss.values())
                    }
                }
                
                json.dump(datos_exportacion, archivo, indent=4, ensure_ascii=False)
            
            print(f"✓ Resultados guardados en {ruta_salida}")
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar resultados: {e}")
            return False
