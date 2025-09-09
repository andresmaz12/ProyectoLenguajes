from ciclo import palabrasReservadas
palabras = palabrasReservadas()

class manejoArchivos:
    def __init__(self, ruta):
        self.ruta = ruta

    #Lectrua del archivo de texto linea por linea, funcionando similar a python o JS
    def lecturaArchivo(self, ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                for numero, linea in enumerate(archivo, start=1):
                    #Metodo para interpretar lo escrito en el texto
                    palabras.cicloPalabras(linea)
        except FileNotFoundError: 
            print("Archvio no encontrado")
        except Exception as e: 
            print(f"ocurrio un error: {e}")

    #Permite que el usuario ingrese lineas de codigo simple guardadas en un archvio de texto plano
    def escrituraArchivos(self, ruta):
        try: 
            with open(ruta, "a", encoding="utf-8") as archivo:
                while True: 
                    linea = input("")
                    if linea.upper() == "Finalizar":
                        break
        except Exception as e:
            print(f"Hubo un error: {e}")
