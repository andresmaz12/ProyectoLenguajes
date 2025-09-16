from ciclo import AnalizadorLexico
palabras = AnalizadorLexico()

class ManejoArchivos:
    def __init__(self, ruta):
        self.ruta = ruta
        self.archivoAbierto = None
        self.numeroDePalabras = 7

    # Solo abre el archivo
    def lecturaArchivo(self, ruta):
        try:
            self.archivoAbierto = open(ruta, "r", encoding="utf-8")
            print(f"Archivo '{ruta}' abierto correctamente")
            return True
        except FileNotFoundError: 
            print("Archivo no encontrado")
            return False
        except Exception as e: 
            print(f"Ocurrió un error: {e}")
            return False

    # Lectura palabra por palabra del archivo ya abierto
    def lecturaPalabraPorPalabra(self):
        if self.archivoAbierto is None:
            print("No hay ningún archivo abierto")
            return
        
        try:
            # Reiniciar el puntero del archivo al inicio
            self.archivoAbierto.seek(0)
            
            for numero, linea in enumerate(self.archivoAbierto, start=1):
                for palabra in linea.split():
                    # Aquí interpretamos cada palabra
                    palabras.clasificar_token(palabra)
                    self.numeroDePalabras += 1
                    #Prueba
                    # print("palabra leida")
                    
        except Exception as e:
            print(f"Ocurrió un error durante la lectura: {e}")

    # Método para cerrar el archivo
    def cerrarArchivo(self):
        if self.archivoAbierto:
            self.archivoAbierto.close()
            self.archivoAbierto = None
            print("Archivo cerrado")

    # Escritura en archivo de texto plano
    def escrituraArchivos(self, ruta):
        try: 
            with open(ruta, "a", encoding="utf-8") as archivo:
                while True: 
                    linea = input("")
                    if linea.upper() == "FINALIZAR":
                        break
                    archivo.write(linea + "\n")
        except Exception as e:
            print(f"Hubo un error: {e}")

