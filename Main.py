from AnalisisLexico import AnalizadorLexico
from AnalizadorGramatical import AnalizadorGramatical
from Formulario import InterfazAnalizador

def main():
    """Función principal que inicializa y ejecuta la aplicación"""
    
    # Inicializar analizador léxico
    analizador_lexico = AnalizadorLexico("Tokens.json")
    
    # Inicializar analizador gramatical (recibe las categorías del léxico)
    analizador_gramatical = AnalizadorGramatical(analizador_lexico.get_tokens_json())
    
    # Crear y mostrar la interfaz
    interfaz = InterfazAnalizador(analizador_lexico, analizador_gramatical)
    
    # Iniciar el loop de la interfaz
    interfaz.iniciar()

if __name__ == "__main__":
    main()