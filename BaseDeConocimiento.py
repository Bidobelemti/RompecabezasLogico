from logic import *
import tkinter as tk
from tkinter import messagebox, scrolledtext
from sympy import sympify, Not

class KnowledgeBaseApp:
    """
    Aplicación para gestionar una base de conocimiento lógica.
    Permite:
    - Agregar sentencias a la base de conocimiento.
    - Mostrar las sentencias en su forma original y en CNF.
    - Validar la veracidad de una sentencia.
    """

    def __init__(self, root):
        """
        Inicializa la interfaz gráfica y la lógica de la aplicación.
        :param root: Ventana principal de tkinter.
        """
        self.root = root
        self.root.title("Base de Conocimiento Lógica")

        # Configuración general
        self.kb = PropKB()
        self.modified_manually = False  # Rastrea si el usuario edita manualmente el texto

        # Configuración de colores y estilos
        bg_color = "#f2f2f2"
        text_color = "#2f2f2f"
        button_color = "#007acc"
        input_color = "#ffffff"
        self.root.config(bg=bg_color)

        # Sección superior: Agregar sentencias
        frame_top = tk.Frame(root, bg=bg_color, pady=10)
        frame_top.pack(fill=tk.X)

        self.entry = tk.Entry(frame_top, bg=input_color, font=("Calibri", 12), width=60)
        self.entry.pack(side=tk.LEFT, padx=10)
        add_button = tk.Button(
            frame_top,
            text="Agregar Sentencia",
            bg=button_color,
            fg="white",
            font=("Calibri", 10, "bold"),
            command=self.add_sentence,
        )
        add_button.pack(side=tk.LEFT, padx=5)

        # Sección central: Sentencias originales y CNF
        frame_middle = tk.Frame(root, bg=bg_color)
        frame_middle.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Textos
        tk.Label(
            frame_middle, text="Sentencias Originales:", bg=bg_color, fg=text_color, font=("Calibri", 11, "bold")
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(
            frame_middle, text="Sentencias en CNF:", bg=bg_color, fg=text_color, font=("Calibri", 11, "bold")
        ).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Cuadros de texto
        self.original_text = scrolledtext.ScrolledText(frame_middle, wrap=tk.WORD, bg=input_color, height=15, width=40)
        self.original_text.grid(row=1, column=0, padx=5, pady=5)
        self.original_text.bind("<<Modified>>", self.on_text_modified)
        self.original_text.bind("<Key>", self.on_key_press)

        self.cnf_text = scrolledtext.ScrolledText(frame_middle, wrap=tk.WORD, bg=input_color, height=15, width=40)
        self.cnf_text.grid(row=1, column=1, padx=5, pady=5)
        self.cnf_text.config(state=tk.DISABLED)

        # Botón para sincronizar sentencias originales
        sync_button = tk.Button(
            frame_middle,
            text="Sincronizar Sentencias",
            bg=button_color,
            fg="white",
            font=("Calibri", 10, "bold"),
            command=self.sync_sentences,
        )
        sync_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Sección inferior: Validación de sentencias
        frame_bottom = tk.Frame(root, bg=bg_color, pady=10)
        frame_bottom.pack(fill=tk.X)

        self.check_entry = tk.Entry(frame_bottom, bg=input_color, font=("Calibri", 12), width=60)
        self.check_entry.pack(side=tk.LEFT, padx=10)
        validate_button = tk.Button(
            frame_bottom,
            text="Validar Sentencia",
            bg=button_color,
            fg="white",
            font=("Calibri", 10, "bold"),
            command=self.validate_sentence,
        )
        validate_button.pack(side=tk.LEFT, padx=5)

    def add_sentence(self):
        """
        Agrega una nueva sentencia a la base de conocimiento y actualiza las vistas.
        """
        sentence = self.entry.get()
        if sentence:
            try:
                # Convierte la entrada a una expresión lógica
                parsed_sentence = sympify(sentence, evaluate=False)
                self.kb.tell(parsed_sentence)
                self.original_text.insert(tk.END, f"{sentence}\n")
                self.update_cnf_view()
                self.entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Sentencia inválida: {e}")

    def update_cnf_view(self):
        """
        Actualiza la vista de las sentencias en forma CNF.
        """
        self.cnf_text.config(state=tk.NORMAL)
        self.cnf_text.delete(1.0, tk.END)
        for clause in self.kb.clauses:
            self.cnf_text.insert(tk.END, f"{clause}\n")
        self.cnf_text.config(state=tk.DISABLED)

    def sync_sentences(self):
        """
        Sincroniza las sentencias originales con la base de conocimiento.
        """
        self.modified_manually = False
        self.kb.clauses = []
        self.original_text.config(bg="white")
        for line in self.original_text.get(1.0, tk.END).strip().split("\n"):
            if line:
                try:
                    self.kb.tell(sympify(line, evaluate=False))
                except Exception as e:
                    messagebox.showerror("Error", f"Sentencia inválida: {e}")
        self.update_cnf_view()

    def validate_sentence(self):
        """
        Verifica si una sentencia es válida o su negación lo es.
        """
        sentence = self.check_entry.get()
        if sentence:
            try:
                parsed_sentence = sympify(sentence, evaluate=False)
                is_true = self.kb.ask_if_true(parsed_sentence)
                is_false = self.kb.ask_if_true(Not(parsed_sentence))
                if is_true != is_false:
                    result = "Verdadera" if is_true else "Falsa"
                    messagebox.showinfo("Resultado", f"La sentencia es {result}.")
                else:
                    messagebox.showinfo("Resultado", "No se puede determinar la validez.")
            except Exception as e:
                messagebox.showerror("Error", f"Sentencia inválida: {e}")

    def on_text_modified(self, event):
        """
        Detecta si el usuario modifica manualmente las sentencias originales.
        """
        if self.modified_manually:
            self.original_text.config(bg="#ffe6e6")
        self.original_text.edit_modified(False)

    def on_key_press(self, event):
        """
        Marca que el texto fue modificado manualmente.
        """
        self.modified_manually = True


if __name__ == "__main__":
    root = tk.Tk()
    app = KnowledgeBaseApp(root)
    root.mainloop()
