from logic import *

import tkinter as tk
from tkinter import messagebox, scrolledtext
from sympy import sympify, Not 

class KnowledgeBaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicacion de Base de Conocimiento")
        
        self.kb = PropKB()
        self.is_manual_update = False  # Variable para rastrear si la actualización es manual

        # Variables para visualizacin de interfaz grafica 
        anchoBoton = 16
        colorBoton = "#b3b5b4"
        colorFondo = "white"
        colorTextInput = "#eeeeee"
        defaultFont = ("Calibri", 11)
        boldFont = ("Calibri", 10)

        root.config(bg=colorFondo)
        # Section to write and send sentences
        self.entry_label = tk.Label(root, bg=colorFondo, text="Agregar una sentencia:")
        self.entry_label.grid(row=0, column=0, padx=10, pady=10)
        self.entry = tk.Entry(root, bg=colorTextInput, width=50)
        self.entry.grid(row=0, column=1, padx=10, pady=10)

        self.add_button = tk.Button(root, text="Agregar", width=anchoBoton, bg=colorBoton, command=self.add_sentence)
        self.add_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        # Section to show original sentences
        self.original_label = tk.Label(root, text="Sentencias originales:", bg=colorFondo)
        self.original_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='w')
        self.original_text = scrolledtext.ScrolledText(root, bg=colorTextInput, width=50, height=10)
        self.original_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        # Bind the <<Modified>> event to a handler function
        self.original_text.bind("<<Modified>>", self.on_text_modified)
        # Bind keyboard events to detect manual modifications
        self.original_text.bind("<Key>", self.on_key_press)

        self.accept_original_text_button = tk.Button(root, text="Actualizar", width=anchoBoton, bg=colorBoton, command=self.accept_original_text)
        self.accept_original_text_button.grid(row=4, column=1, padx=10, pady=10, sticky='e')

        # Section to show CNF sentences
        self.cnf_label = tk.Label(root, bg=colorFondo, text="Sentencias en CNF:")
        self.cnf_label.grid(row=2, column=2, columnspan=2, padx=10, pady=10, sticky='w')
        self.cnf_text = scrolledtext.ScrolledText(root, bg=colorTextInput, width=50, height=10)
        self.cnf_text.grid(row=3, column=2, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.cnf_text.config(state=tk.DISABLED)

        # Section to check sentence validity
        self.check_label = tk.Label(root, bg=colorFondo, text="Sentencia:")
        self.check_label.grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.check_entry = tk.Entry(root, bg=colorTextInput, width=50)
        self.check_entry.grid(row=0, column=3, padx=10, pady=10, sticky='nsew')

        self.valid_button = tk.Button(root, text="Validar sentencia", width=anchoBoton, bg=colorBoton, command=self.check_validity)
        self.valid_button.grid(row=1, column=3, padx=10, pady=10, sticky="e")

        # Se cambian las fuentes de todos los elementos
        self.entry_label.config(font=defaultFont)
        self.entry.config(font=defaultFont)
        self.add_button.config(font=boldFont)
        self.original_label.config(font=defaultFont)
        self.original_text.config(font=defaultFont)
        self.accept_original_text_button.config(font=boldFont)
        self.cnf_label.config(font=defaultFont)
        self.cnf_text.config(font=defaultFont)
        self.check_label.config(font=defaultFont)
        self.check_entry.config(font=defaultFont)
        self.valid_button.config(font=boldFont)

    def add_sentence(self):
        sentence = self.entry.get()
        if len(sentence) != 0:
            self.kb.tell(sympify(sentence))
            self.update_original_text(sentence)
        self.update_cnf_text()
        self.entry.delete(0, tk.END)

    def update_original_text(self, sentence):
        self.original_text.insert(tk.END, f"{sentence}\n")

    def update_cnf_text(self):
        self.cnf_text.config(state=tk.NORMAL)
        self.cnf_text.delete('1.0', tk.END)
        for cnf_sentence in self.kb.clauses:
            self.cnf_text.insert(tk.END, f"{cnf_sentence}\n")
        self.cnf_text.config(state=tk.DISABLED)

    def accept_original_text(self):
        self.original_text.config(background="white")
        self.is_manual_update = False 
        self.kb.clauses = []
        new_clauses = self.original_text.get('1.0', tk.END) 
        list_clauses = new_clauses.split('\n')
        for l in list_clauses:
            if len(l) != 0:
                self.kb.tell(sympify(l))
        self.add_sentence()
        self.is_manual_update = False 


    def check_validity(self):
        sentence = self.check_entry.get()
        # Implementar lógica de verificación de validez
        
        # resultS -> result of sentence
        # resultNS -> result of not sentence
        resultS = False 
        resultNS = False 
        if len(sentence) != 0:
            resultS = self.kb.ask_if_true(sympify(sentence))
            resultNS = self.kb.ask_if_true(Not(sympify(sentence)))
        
        if resultS != resultNS:
            messagebox.showinfo("Resultado", f"La sentencia es {resultS}")
        else:
            messagebox.showinfo("Resultado", "No se puede determinar la validez de la sentencia.")
    
    def on_text_modified(self, event):
        if self.is_manual_update:
            self.original_text.config(background="#ff9393")
        # Reset the modified flag
        self.original_text.edit_modified(False)

    def on_key_press(self, event):
        # Set the modified flag to True to trigger <<Modified>> event
        self.is_manual_update = True

if __name__ == "__main__":
    root = tk.Tk()
    app = KnowledgeBaseApp(root)
    root.mainloop()
