"""
frames/config.py
Configuración del sistema, descuentos y plantilla de recibos
"""
from tkinter import ttk, messagebox
import tkinter as tk
from datetime import datetime


class ConfigFrame(ttk.Frame):
    """Frame de configuración del sistema."""
    
    def __init__(self, parent, app):
        super().__init__(parent, padding="10")
        self.app = app
        self.db = app.db
        
        # Notebook con pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, pady=10)
        
        # Pestaña 1: Descuentos
        disc_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(disc_tab, text="Descuentos")
        self.create_discount_tab(disc_tab)
        
        # Pestaña 2: Plantilla de Recibo
        receipt_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(receipt_tab, text="Plantilla de Recibo")
        self.create_receipt_tab(receipt_tab)

    def create_discount_tab(self, parent):
        """Crea la pestaña de gestión de descuentos."""
        parent.grid_columnconfigure(0, weight=2)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        list_frame = ttk.Frame(parent, padding=10, relief="groove")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        form_frame = ttk.Frame(parent, padding=10, relief="groove")
        form_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Lista de descuentos
        ttk.Label(
            list_frame, 
            text="Listado de Descuentos", 
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 10))
        
        self.disc_tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Nombre", "Tipo", "Porcentaje"),
            show="headings",
            height=12
        )
        
        self.disc_tree.heading("ID", text="ID")
        self.disc_tree.heading("Nombre", text="Nombre")
        self.disc_tree.heading("Tipo", text="Tipo")
        self.disc_tree.heading("Porcentaje", text="Porcentaje")
        
        self.disc_tree.column("ID", width=50, anchor="center")
        self.disc_tree.column("Nombre", width=200)
        self.disc_tree.column("Tipo", width=100)
        self.disc_tree.column("Porcentaje", width=100, anchor="center")
        
        self.disc_tree.bind('<<TreeviewSelect>>', self.select_discount)
        self.disc_tree.pack(fill="both", expand=True, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Nuevo Descuento", 
            command=self.reset_discount_form
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Eliminar", 
            command=self.delete_discount
        ).pack(side="left", padx=5)
        
        self.load_discounts()
        
        # Formulario de descuento
        ttk.Label(
            form_frame, 
            text="Formulario de Descuento", 
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        self.disc_id = tk.StringVar(value="")
        self.disc_nombre = tk.StringVar()
        self.disc_porcentaje = tk.StringVar()
        self.disc_tipo = tk.StringVar(value="Docena")
        
        ttk.Label(form_frame, text="Nombre:").grid(row=1, column=0, sticky="w", padx=5, pady=8)
        ttk.Entry(form_frame, textvariable=self.disc_nombre, width=25).grid(
            row=1, column=1, sticky="ew", padx=5, pady=8
        )
        
        ttk.Label(form_frame, text="Porcentaje (%):").grid(row=2, column=0, sticky="w", padx=5, pady=8)
        ttk.Entry(form_frame, textvariable=self.disc_porcentaje, width=25).grid(
            row=2, column=1, sticky="ew", padx=5, pady=8
        )
        
        ttk.Label(form_frame, text="Tipo:").grid(row=3, column=0, sticky="w", padx=5, pady=8)
        ttk.Combobox(
            form_frame, 
            textvariable=self.disc_tipo, 
            values=["Docena", "Mayorista", "Producto"], 
            state='readonly',
            width=23
        ).grid(row=3, column=1, sticky="ew", padx=5, pady=8)
        
        ttk.Button(
            form_frame, 
            text="Guardar Descuento", 
            command=self.save_discount
        ).grid(row=4, column=0, columnspan=2, pady=20, sticky="ew")

    def load_discounts(self):
        """Carga todos los descuentos."""
        for item in self.disc_tree.get_children():
            self.disc_tree.delete(item)
        
        discounts = self.db.fetch("SELECT id, nombre, tipo, porcentaje FROM Descuentos")
        
        for disc in discounts:
            self.disc_tree.insert(
                "", "end", 
                values=(disc[0], disc[1], disc[2], f"{int(disc[3]*100)}%")
            )

    def select_discount(self, event):
        """Carga el descuento seleccionado en el formulario."""
        selected_item = self.disc_tree.focus()
        if not selected_item:
            return
        
        values = self.disc_tree.item(selected_item, 'values')
        self.disc_id.set(values[0])
        self.disc_nombre.set(values[1])
        self.disc_tipo.set(values[2])
        self.disc_porcentaje.set(values[3].strip('%'))

    def reset_discount_form(self):
        """Limpia el formulario de descuento."""
        self.disc_id.set("")
        self.disc_nombre.set("")
        self.disc_porcentaje.set("")
        self.disc_tipo.set("Docena")

    def save_discount(self):
        """Guarda o actualiza un descuento."""
        nombre = self.disc_nombre.get()
        porcentaje = self.disc_porcentaje.get()
        tipo = self.disc_tipo.get()
        
        if not all([nombre, porcentaje, tipo]):
            messagebox.showerror("Error", "Complete todos los campos.")
            return
        
        try:
            pct = float(porcentaje) / 100.0
            if pct <= 0 or pct >= 1:
                messagebox.showerror("Error", "El porcentaje debe estar entre 1 y 99.")
                return
        except ValueError:
            messagebox.showerror("Error", "El porcentaje debe ser un número válido.")
            return
        
        if self.disc_id.get():
            # Actualizar
            query = "UPDATE Descuentos SET nombre=?, tipo=?, porcentaje=? WHERE id=?"
            self.db.execute(query, (nombre, tipo, pct, self.disc_id.get()))
            messagebox.showinfo("Éxito", "Descuento actualizado.")
        else:
            # Insertar
            query = "INSERT INTO Descuentos (nombre, tipo, porcentaje) VALUES (?, ?, ?)"
            self.db.execute(query, (nombre, tipo, pct))
            messagebox.showinfo("Éxito", "Descuento agregado.")
        
        self.load_discounts()
        self.reset_discount_form()

    def delete_discount(self):
        """Elimina el descuento seleccionado."""
        selected_item = self.disc_tree.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un descuento primero.")
            return
        
        disc_id = self.disc_tree.item(selected_item, 'values')[0]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el descuento ID {disc_id}?"):
            self.db.execute("DELETE FROM Descuentos WHERE id = ?", (disc_id,))
            messagebox.showinfo("Éxito", "Descuento eliminado.")
            self.load_discounts()
            self.reset_discount_form()

    def create_receipt_tab(self, parent):
        """Crea la pestaña de configuración de recibo."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        ttk.Label(
            parent, 
            text="Editor de Plantilla HTML de Recibo", 
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        ttk.Label(
            parent,
            text="Variables disponibles: {{ID_VENTA}}, {{FECHA}}, {{TOTAL}}, {{MONTO_PAGADO}}, {{VUELTO}}, {{NOMBRE_NEGOCIO}}",
            font=('Arial', 9),
            foreground="#666"
        ).grid(row=0, column=1, pady=(0, 10), sticky="w", padx=20)
        
        # Editor de texto
        self.template_text = tk.Text(parent, height=18, width=70, font=('Courier', 10))
        self.template_text.grid(row=1, column=0, sticky="nsew", pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.template_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=10)
        self.template_text.configure(yscrollcommand=scrollbar.set)
        
        # Cargar plantilla existente
        template = self.db.get_config('recibo_template', self.db.default_receipt_template())
        self.template_text.insert(tk.END, template)
        
        # Botones
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        
        ttk.Button(
            btn_frame, 
            text="Vista Previa", 
            command=self.preview_receipt
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Guardar Plantilla", 
            command=self.save_receipt_template
        ).pack(side="right", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Restaurar Plantilla Original", 
            command=self.restore_default_template
        ).pack(side="right", padx=5)

    def preview_receipt(self):
        """Muestra una vista previa del recibo."""
        template_content = self.template_text.get(1.0, tk.END).strip()
        
        # Datos de ejemplo
        html_preview = template_content
        html_preview = html_preview.replace("{{NOMBRE_NEGOCIO}}", "Mi Negocio ERP")
        html_preview = html_preview.replace("{{ID_VENTA}}", "V-20250929-001")
        html_preview = html_preview.replace("{{FECHA}}", datetime.now().strftime("%d/%m/%Y %H:%M"))
        html_preview = html_preview.replace("{{TOTAL}}", "150.00")
        html_preview = html_preview.replace("{{MONTO_PAGADO}}", "200.00")
        html_preview = html_preview.replace("{{VUELTO}}", "50.00")
        
        # Items de ejemplo
        items_html = """
            <div class="item"><span>Monitor 27"</span><span>1 / $120.00</span></div>
            <div class="item"><span>Mouse Gamer</span><span>2 / $30.00</span></div>
        """
        html_preview = html_preview.replace("<!-- ITEMS_PLACEHOLDER -->", items_html)
        
        # Ventana de vista previa
        preview_win = tk.Toplevel(self.app)
        preview_win.title("Vista Previa de Recibo")
        preview_win.geometry("400x600")
        
        ttk.Label(
            preview_win, 
            text="Vista Previa Simplificada", 
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        # Mostrar HTML renderizado (simplificado)
        preview_text = tk.Text(preview_win, height=30, width=50, font=('Courier', 9))
        preview_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Limpiar HTML para vista previa
        import re
        clean_text = re.sub('<[^<]+?>', '', html_preview)
        clean_text = clean_text.replace('&nbsp;', ' ')
        preview_text.insert(tk.END, clean_text)
        preview_text.config(state=tk.DISABLED)

    def save_receipt_template(self):
        """Guarda la plantilla de recibo."""
        template_content = self.template_text.get(1.0, tk.END).strip()
        
        if not template_content:
            messagebox.showerror("Error", "La plantilla no puede estar vacía.")
            return
        
        self.db.set_config('recibo_template', template_content)
        messagebox.showinfo("Éxito", "Plantilla guardada correctamente.")

    def restore_default_template(self):
        """Restaura la plantilla original."""
        if messagebox.askyesno("Confirmar", "¿Restaurar la plantilla original?"):
            default_template = self.db.default_receipt_template()
            self.template_text.delete(1.0, tk.END)
            self.template_text.insert(tk.END, default_template)
            messagebox.showinfo("Éxito", "Plantilla restaurada.")