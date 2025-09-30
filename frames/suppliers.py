"""
frames/suppliers.py
Gestión completa de proveedores con CRUD
"""
from tkinter import ttk, messagebox
import tkinter as tk


class SupplierFrame(ttk.Frame):
    """Frame para gestión de proveedores."""
    
    def __init__(self, parent, app):
        super().__init__(parent, padding="10")
        self.app = app
        self.db = app.db
        
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.list_frame = ttk.Frame(self, padding="10", relief="groove")
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.form_frame = ttk.Frame(self, padding="10", relief="groove")
        self.form_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.create_supplier_list()
        self.create_supplier_form()
        self.load_suppliers()

    def create_supplier_list(self):
        """Crea la lista de proveedores."""
        ttk.Label(
            self.list_frame, 
            text="Listado de Proveedores", 
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 10))
        
        # Treeview
        self.tree = ttk.Treeview(
            self.list_frame,
            columns=("ID", "Nombre", "Contacto", "Teléfono"),
            show="headings",
            height=15
        )
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre Proveedor")
        self.tree.heading("Contacto", text="Persona de Contacto")
        self.tree.heading("Teléfono", text="Teléfono")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nombre", width=200)
        self.tree.column("Contacto", width=150)
        self.tree.column("Teléfono", width=120)
        
        self.tree.bind('<<TreeviewSelect>>', self.select_supplier)
        self.tree.pack(fill="both", expand=True, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(self.list_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Nuevo Proveedor", 
            command=self.reset_form
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Eliminar", 
            command=self.delete_supplier
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Exportar CSV", 
            command=lambda: self.app.file_manager.export_data("Proveedores")
        ).pack(side="right", padx=5)

    def create_supplier_form(self):
        """Crea el formulario de proveedor."""
        ttk.Label(
            self.form_frame, 
            text="Formulario de Proveedor", 
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Variables
        self.sup_id = tk.StringVar(value="")
        self.nombre = tk.StringVar()
        self.contacto = tk.StringVar()
        self.telefono = tk.StringVar()
        
        # Campos
        fields = [
            ("Nombre Empresa:", self.nombre),
            ("Persona Contacto:", self.contacto),
            ("Teléfono:", self.telefono)
        ]
        
        row = 1
        for label_text, var in fields:
            ttk.Label(self.form_frame, text=label_text).grid(
                row=row, column=0, sticky="w", padx=5, pady=8
            )
            ttk.Entry(self.form_frame, textvariable=var, width=30).grid(
                row=row, column=1, sticky="ew", padx=5, pady=8
            )
            row += 1
        
        # Botón guardar
        ttk.Button(
            self.form_frame, 
            text="Guardar Proveedor", 
            command=self.save_supplier
        ).grid(row=row, column=0, columnspan=2, pady=20, sticky="ew")

    def load_suppliers(self):
        """Carga todos los proveedores."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        suppliers = self.db.fetch(
            "SELECT id, nombre, contacto, telefono FROM Proveedores ORDER BY id DESC"
        )
        
        for sup in suppliers:
            self.tree.insert("", "end", values=sup)

    def select_supplier(self, event):
        """Carga datos del proveedor seleccionado."""
        selected_item = self.tree.focus()
        if not selected_item:
            return
        
        values = self.tree.item(selected_item, 'values')
        self.sup_id.set(values[0])
        self.nombre.set(values[1])
        self.contacto.set(values[2])
        self.telefono.set(values[3])

    def reset_form(self):
        """Limpia el formulario."""
        self.sup_id.set("")
        self.nombre.set("")
        self.contacto.set("")
        self.telefono.set("")

    def save_supplier(self):
        """Guarda o actualiza un proveedor."""
        nombre = self.nombre.get()
        contacto = self.contacto.get()
        telefono = self.telefono.get()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return
        
        if self.sup_id.get():
            # Actualizar
            query = "UPDATE Proveedores SET nombre=?, contacto=?, telefono=? WHERE id=?"
            self.db.execute(query, (nombre, contacto, telefono, self.sup_id.get()))
            messagebox.showinfo("Éxito", "Proveedor actualizado.")
        else:
            # Insertar
            query = "INSERT INTO Proveedores (nombre, contacto, telefono) VALUES (?, ?, ?)"
            self.db.execute(query, (nombre, contacto, telefono))
            messagebox.showinfo("Éxito", "Proveedor agregado.")
        
        self.load_suppliers()
        self.reset_form()

    def delete_supplier(self):
        """Elimina el proveedor seleccionado."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor primero.")
            return
        
        sup_id = self.tree.item(selected_item, 'values')[0]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el proveedor ID {sup_id}?"):
            self.db.execute("DELETE FROM Proveedores WHERE id = ?", (sup_id,))
            messagebox.showinfo("Éxito", "Proveedor eliminado.")
            self.load_suppliers()
            self.reset_form()