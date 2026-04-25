import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils import format_json, load_json_file, save_json_file, get_stats

BG = "#1e1e2e"
BG2 = "#16213e"
BG3 = "#0f3460"
FG = "#e0e0e0"
FG2 = "#9e9e9e"
ACCENT = "#1976d2"
SUCCESS = "#43a047"
ERROR = "#e53935"
FONT_MONO = ("Consolas", 11)
FONT_UI = ("Segoe UI", 10)


class JSONifyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSONify")
        self.root.geometry("1200x700")
        self.root.configure(bg=BG)
        self.root.minsize(800, 500)
        self._build_toolbar()
        self._build_main()
        self._build_statusbar()
        self._bind_shortcuts()

    def _build_toolbar(self):
        toolbar = tk.Frame(self.root, bg=BG3, pady=8)
        toolbar.pack(fill=tk.X)

        title = tk.Label(toolbar, text="JSONify", bg=BG3, fg=FG,
                         font=("Segoe UI", 13, "bold"))
        title.pack(side=tk.LEFT, padx=16)

        sep = tk.Frame(toolbar, bg=FG2, width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=4)

        buttons = [
            ("Formatear", ACCENT, self.format_json),
            ("Limpiar", "#424242", self.clear),
            ("Copiar", "#00796b", self.copy_result),
            ("Cargar archivo", "#6a1b9a", self.load_file),
            ("Guardar", "#1565c0", self.save_file),
        ]

        for text, color, cmd in buttons:
            btn = tk.Button(
                toolbar, text=text, bg=color, fg="white",
                font=FONT_UI, relief=tk.FLAT, padx=12, pady=4,
                cursor="hand2", activebackground=color,
                activeforeground="white", command=cmd
            )
            btn.pack(side=tk.LEFT, padx=4)

        expand_btn = tk.Button(
            toolbar, text="Expandir todo", bg=BG2, fg=FG2,
            font=FONT_UI, relief=tk.FLAT, padx=12, pady=4,
            cursor="hand2", activebackground=BG2,
            activeforeground=FG, command=self.expand_all
        )
        expand_btn.pack(side=tk.RIGHT, padx=4)

        collapse_btn = tk.Button(
            toolbar, text="Colapsar todo", bg=BG2, fg=FG2,
            font=FONT_UI, relief=tk.FLAT, padx=12, pady=4,
            cursor="hand2", activebackground=BG2,
            activeforeground=FG, command=self.collapse_all
        )
        collapse_btn.pack(side=tk.RIGHT, padx=4)

    def _build_main(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = tk.Frame(main, bg=BG2, bd=0)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        lbl_in = tk.Label(left, text="JSON de entrada", bg=BG2, fg=FG2, font=FONT_UI)
        lbl_in.pack(anchor=tk.W, padx=8, pady=(8, 2))

        self.input_text = tk.Text(
            left, bg=BG2, fg=FG, font=FONT_MONO,
            insertbackground=FG, selectbackground=ACCENT,
            relief=tk.FLAT, padx=10, pady=10, wrap=tk.NONE,
            undo=True
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        self.input_text.bind("<KeyRelease>", self.on_input_change)

        scroll_in = ttk.Scrollbar(left, orient=tk.VERTICAL,
                                   command=self.input_text.yview)
        self.input_text.configure(yscrollcommand=scroll_in.set)
        scroll_in.pack(side=tk.RIGHT, fill=tk.Y)

        right = tk.Frame(main, bg=BG)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        notebook = ttk.Notebook(right)
        notebook.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG3, foreground=FG2,
                         padding=[12, 6], font=FONT_UI)
        style.map("TNotebook.Tab", background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        text_tab = tk.Frame(notebook, bg=BG2)
        notebook.add(text_tab, text="Texto formateado")

        self.output_text = tk.Text(
            text_tab, bg=BG2, fg=FG, font=FONT_MONO,
            insertbackground=FG, selectbackground=ACCENT,
            relief=tk.FLAT, padx=10, pady=10, wrap=tk.NONE,
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        self.output_text.tag_configure("key", foreground="#82aaff")
        self.output_text.tag_configure("string", foreground="#c3e88d")
        self.output_text.tag_configure("number", foreground="#f78c6c")
        self.output_text.tag_configure("boolean", foreground="#ffcb6b")
        self.output_text.tag_configure("null", foreground="#ff5370")
        self.output_text.tag_configure("error", foreground=ERROR)

        scroll_out = ttk.Scrollbar(text_tab, orient=tk.VERTICAL,
                                    command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scroll_out.set)
        scroll_out.pack(side=tk.RIGHT, fill=tk.Y)

        tree_tab = tk.Frame(notebook, bg=BG2)
        notebook.add(tree_tab, text="Árbol")

        style.configure("Treeview", background=BG2, foreground=FG,
                         fieldbackground=BG2, borderwidth=0, font=FONT_MONO)
        style.configure("Treeview.Heading", background=BG3, foreground=FG,
                         font=FONT_UI)
        style.map("Treeview", background=[("selected", ACCENT)])

        self.tree = ttk.Treeview(tree_tab, show="tree headings")
        self.tree["columns"] = ("value",)
        self.tree.column("#0", width=300)
        self.tree.column("value", width=400)
        self.tree.heading("#0", text="Clave")
        self.tree.heading("value", text="Valor")
        self.tree.pack(fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_tab, orient=tk.VERTICAL,
                                     command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_statusbar(self):
        self.status_bar = tk.Frame(self.root, bg=BG3, pady=4)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = tk.Label(
            self.status_bar, text="Listo", bg=BG3, fg=FG2, font=FONT_UI
        )
        self.status_label.pack(side=tk.LEFT, padx=12)

        self.stats_label = tk.Label(
            self.status_bar, text="Líneas: 0 | Caracteres: 0",
            bg=BG3, fg=FG2, font=FONT_UI
        )
        self.stats_label.pack(side=tk.RIGHT, padx=12)

    def _bind_shortcuts(self):
        self.root.bind("<Control-Return>", lambda e: self.format_json())
        self.root.bind("<Control-o>", lambda e: self.load_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())

    def on_input_change(self, event=None):
        text = self.input_text.get("1.0", tk.END).strip()
        lines, chars = get_stats(text)
        self.stats_label.config(text=f"Líneas: {lines} | Caracteres: {chars}")

    def format_json(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            self._set_status("Pega un JSON en el panel izquierdo", ERROR)
            return
        result, error = format_json(text)
        if error:
            self._set_output(f"Error: {error}", is_error=True)
            self._set_status(f"JSON inválido — {error}", ERROR)
        else:
            self._set_output(result)
            self._set_status("JSON formateado correctamente", SUCCESS)
            self._build_tree(json.loads(text))

    def _set_output(self, text, is_error=False):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        if is_error:
            self.output_text.insert(tk.END, text, "error")
        else:
            self._insert_colored(text)
        self.output_text.config(state=tk.DISABLED)

    def _insert_colored(self, text):
        import re
        lines = text.split("\n")
        for line in lines:
            key_match = re.match(r'^(\s*)"([^"]+)"(\s*:\s*)(.*)', line)
            if key_match:
                self.output_text.insert(tk.END, key_match.group(1))
                self.output_text.insert(tk.END,
                    f'"{key_match.group(2)}"', "key")
                self.output_text.insert(tk.END, key_match.group(3))
                value = key_match.group(4).rstrip(",")
                trailing = "," if key_match.group(4).endswith(",") else ""
                self._insert_value(value)
                self.output_text.insert(tk.END, trailing + "\n")
            else:
                self.output_text.insert(tk.END, line + "\n")

    def _insert_value(self, value):
        v = value.strip()
        if v.startswith('"'):
            self.output_text.insert(tk.END, value, "string")
        elif v in ("true", "false"):
            self.output_text.insert(tk.END, value, "boolean")
        elif v == "null":
            self.output_text.insert(tk.END, value, "null")
        elif v.lstrip("-").replace(".", "").isdigit():
            self.output_text.insert(tk.END, value, "number")
        else:
            self.output_text.insert(tk.END, value)

    def _build_tree(self, data, parent="", key="root"):
        self.tree.delete(*self.tree.get_children())
        self._insert_tree(data, "", "root")

    def _insert_tree(self, data, parent, key):
        if isinstance(data, dict):
            node = self.tree.insert(parent, tk.END, text=f"{key}", values=("{...}",))
            for k, v in data.items():
                self._insert_tree(v, node, k)
        elif isinstance(data, list):
            node = self.tree.insert(parent, tk.END, text=f"{key}", values=(f"[{len(data)} items]",))
            for i, v in enumerate(data):
                self._insert_tree(v, node, f"[{i}]")
        else:
            self.tree.insert(parent, tk.END, text=str(key), values=(str(data),))

    def expand_all(self):
        for item in self.tree.get_children():
            self.tree.item(item, open=True)
            self._expand_recursive(item)

    def _expand_recursive(self, item):
        for child in self.tree.get_children(item):
            self.tree.item(child, open=True)
            self._expand_recursive(child)

    def collapse_all(self):
        for item in self.tree.get_children():
            self.tree.item(item, open=False)

    def clear(self):
        self.input_text.delete("1.0", tk.END)
        self._set_output("")
        self.tree.delete(*self.tree.get_children())
        self._set_status("Listo", FG2)
        self.stats_label.config(text="Líneas: 0 | Caracteres: 0")

    def copy_result(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self._set_status("Copiado al portapapeles", SUCCESS)
        else:
            self._set_status("No hay nada que copiar", ERROR)

    def load_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            content, error = load_json_file(filepath)
            if error:
                self._set_status(f"Error al cargar: {error}", ERROR)
            else:
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, content)
                self._set_status(f"Archivo cargado", SUCCESS)
                self.on_input_change()

    def save_file(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if not text:
            self._set_status("No hay nada que guardar", ERROR)
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filepath:
            ok, error = save_json_file(filepath, text)
            if ok:
                self._set_status(f"Guardado en {filepath}", SUCCESS)
            else:
                self._set_status(f"Error al guardar: {error}", ERROR)

    def _set_status(self, text, color=None):
        self.status_label.config(text=text, fg=color or FG2)

import json