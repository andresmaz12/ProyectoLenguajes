import tkinter as tk

def crear_tabla():

    for widget in frame_tabla.winfo_children():
        widget.destroy()

    try:
        filas = int(entry_filas.get())  
    except ValueError:
        return

    columnas = ["TOKEN", "TIPO", "CANTIDAD"]

    for col, texto in enumerate(columnas):
        lbl = tk.Label(frame_tabla, text=texto, bg="black", fg="white", width=20, borderwidth=1, relief="solid")
        lbl.grid(row=0, column=col, sticky="nsew")


    for fila in range(1, filas + 1):
        for col in range(3):  
            e = tk.Entry(frame_tabla, width=20, borderwidth=1, relief="solid")
            e.grid(row=fila, column=col, sticky="nsew")


ventana = tk.Tk()
ventana.title("Tabla ")

tk.Label(ventana, text="nuemero de filas desadas:").pack(pady=5)
entry_filas = tk.Entry(ventana)
entry_filas.pack(pady=5)

btn_crear = tk.Button(ventana, text="Crear Tabla", command=crear_tabla)
btn_crear.pack(pady=5)

frame_tabla = tk.Frame(ventana)
frame_tabla.pack(pady=10)

ventana.mainloop()