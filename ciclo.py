tokenss = {}
try:
    with open("Tokens.json", "r", encoding="utf-8") as archivo:
        tokens_json = json.load(archivo)
    print("✓ JSON de tokens cargado correctamente")
except FileNotFoundError:
    print("❌ Error: No se encontró el archivo Tokens.json")
    exit()
except json.JSONDecodeError:
    print("❌ Error: El archivo Tokens.json tiene formato inválido")
    exit()

def clasificar_token(token, categorias):

    if token in categorias["Preservada"]:
        return "Preservada"
    if token in categorias["operadores"]:
        return "operadores"
    if token in categorias["signos"]:
        return "signos"
    if token in categorias["numeros"]:
        return "numeros"
    if token.isidentifier():
        return "identificadores"
    if re.match(r"^\d+\.\d+$|^\d+$", token):
        return "numeros"
    if token == " ":
        return "espacio"
    
    return "desconocido"

def analizar_archivo(ruta_txt, categorias):
    if not os.path.exists(ruta_txt):
        print(f"❌ Error: El archivo {ruta_txt} no existe")
        return
    
    file_size = os.path.getsize(ruta_txt)
    print(f"✓ Tamaño del archivo: {file_size} bytes")
    
    if file_size == 0:
        print("❌ El archivo está vacío")
        return
    print("-" * 50)
    
    with open(ruta_txt, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()
        print(f"✓ Número de líneas en el archivo: {len(lineas)}")
        
        for numero, linea in enumerate(lineas, start=1):
            linea = linea.strip()
           
            if not linea:
                print(f"Línea {numero}: [vacía] - saltando")
                continue

            print(f"\nLínea {numero}: '{linea}'")
            tokens = re.findall(r"[A-Za-z_]\w*|\d+|\d+\.\d+|==|!=|<=|>=|[+\-*/=()]|[\{\};,]", linea)
            
            if not tokens:
                print(f"  No se encontraron tokens en la línea {numero}")
                continue
                
            for token in tokens:
                categoria = clasificar_token(token, categorias)
                if categoria == "desconocido":
                    print(f"  '{token}' → ¡ATENCIÓN! Token desconocido")
                elif categoria == "espacio":
                    continue
                else:
                    if token in tokenss:
                        tokenss[token]["Cantidad"] += 1
                    else:
                        tokenss[token] = {"Token": token, "Tipo":categoria, "Cantidad": 1}
                    print(f"  '{token}' → Tipo: {categoria}, Cantidad actual: {tokenss[token]['Cantidad']}")

ruta_archivo = r"C:\Users\USUARIO\Desktop\asd.txt"

print(f"Buscando archivo en: {ruta_archivo}")
print()

analizar_archivo(ruta_archivo, tokens_json)

print("\n" + "="*50)
print("Análisis completado.")