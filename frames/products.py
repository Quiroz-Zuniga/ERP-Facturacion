"""
frames/products.py
Gestión completa de productos con CRUD y importación/exportación
"""
from tkinter import ttk, messagebox
import tkinter as tk
import os


class ProductFrame(ttk.Frame):
    """Frame para gestión de productos con CRUD completo."""
    
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
        
        self.create_product_list()
        self.create_product_form()
        self.load_products()

    def create_product_list(self):
        """Crea la lista de productos con búsqueda."""
        ttk.Label(
            self.list_frame, 
            text="Listado de Productos", 
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 10))
        
        # Barra de búsqueda
        search_frame = ttk.Frame(self.list_frame)
        search_frame.pack(fill="x", pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5, fill="x", expand=True)
        search_entry.bind('<KeyRelease>', self.filter_products)
        
        # Treeview de productos
        self.tree = ttk.Treeview(
            self.list_frame,
            columns=("ID", "Nombre", "Precio", "Stock", "Proveedor"),
            show="headings",
            height=15
        )
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre del Producto")
        self.tree.heading("Precio", text="Precio")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Proveedor", text="Proveedor")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Nombre", width=250)
        self.tree.column("Precio", width=100, anchor="center")
        self.tree.column("Stock", width=80, anchor="center")
        self.tree.column("Proveedor", width=100, anchor="center")
        
        self.tree.bind('<<TreeviewSelect>>', self.select_product)
        self.tree.pack(fill="both", expand=True, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Botones de acción
        btn_frame = ttk.Frame(self.list_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Nuevo Producto", 
            command=self.reset_form
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Eliminar", 
            command=self.delete_product
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Importar CSV", 
            command=lambda: self.app.file_manager.import_products(self)
        ).pack(side="right", padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Exportar CSV", 
            command=lambda: self.app.file_manager.export_data("Productos")
        ).pack(side="right", padx=5)

    def create_product_form(self):
        """Crea el formulario de producto."""
        ttk.Label(
            self.form_frame, 
            text="Formulario de Producto", 
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Variables
        self.product_id = tk.StringVar(value="")
        self.nombre = tk.StringVar()
        self.precio = tk.StringVar()
        self.stock = tk.StringVar()
        self.proveedor_id = tk.StringVar(value="1")
        self.imagen_path = tk.StringVar()
        
        # Campos del formulario
        fields = [
            ("Nombre:", self.nombre),
            ("Precio (USD):", self.precio),
            ("Stock:", self.stock),
            ("Proveedor ID:", self.proveedor_id),
            ("Ruta Imagen:", self.imagen_path)
        ]
        
        row = 1
        for label_text, var in fields:
            ttk.Label(self.form_frame, text=label_text).grid(
                row=row, column=0, sticky="w", padx=5, pady=5
            )
            ttk.Entry(self.form_frame, textvariable=var, width=25).grid(
                row=row, column=1, sticky="ew", padx=5, pady=5
            )
            row += 1
        
        # Campo de descripción (Text widget)
        ttk.Label(self.form_frame, text="Descripción:").grid(
            row=row, column=0, sticky="nw", padx=5, pady=5
        )
        self.desc_text = tk.Text(self.form_frame, height=4, width=25, font=('Arial', 10))
        self.desc_text.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Indicador de imagen
        self.image_label = ttk.Label(
            self.form_frame, 
            text="[Sin Imagen]", 
            relief="sunken", 
            anchor="center"
        )
        self.image_label.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        row += 1
        
        # Botón guardar
        ttk.Button(
            self.form_frame, 
            text="Guardar Producto", 
            command=self.save_product
        ).grid(row=row, column=0, columnspan=2, pady=20, sticky="ew")

    def load_products(self):
        """Carga todos los productos en el Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        products = self.db.fetch(
            "SELECT id, nombre, precio, stock, proveedor_id FROM Productos ORDER BY id DESC"
        )
        
        for prod in products:
            self.tree.insert("", "end", values=prod)

    def filter_products(self, event=None):
        """Filtra productos según búsqueda."""
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.load_products()
            return
        
        products = self.db.fetch(
            "SELECT id, nombre, precio, stock, proveedor_id FROM Productos"
        )
        
        for prod in products:
            if search_term in prod[1].lower():
                self.tree.insert("", "end", values=prod)

    def select_product(self, event):
        """Carga datos del producto seleccionado en el formulario."""
        selected_item = self.tree.focus()
        if not selected_item:
            return
        
        values = self.tree.item(selected_item, 'values')
        product_id = values[0]
        
        full_data = self.db.fetch(
            "SELECT nombre, precio, stock, descripcion, proveedor_id, imagen_path FROM Productos WHERE id = ?",
            (product_id,)
        )
        
        if not full_data:
            return
        
        full_data = full_data[0]
        
        self.product_id.set(product_id)
        self.nombre.set(full_data[0])
        self.precio.set(full_data[1])
        self.stock.set(full_data[2])
        self.proveedor_id.set(full_data[4])
        self.imagen_path.set(full_data[5] or "")
        
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(tk.END, full_data[3] or "")
        
        self.update_image_display(full_data[5])

    def update_image_display(self, path):
        """Actualiza el indicador de imagen."""
        if path:
            self.image_label.config(text=f"Imagen: {os.path.basename(path)}")
        else:
            self.image_label.config(text="[Sin Imagen]")

    def reset_form(self):
        """Limpia el formulario."""
        self.product_id.set("")
        self.nombre.set("")
        self.precio.set("")
        self.stock.set("")
        self.proveedor_id.set("1")
        self.imagen_path.set("")
        self.desc_text.delete(1.0, tk.END)
        self.update_image_display(None)

    def save_product(self):
        """Guarda o actualiza un producto."""
        nombre = self.nombre.get()
        precio = self.precio.get()
        stock = self.stock.get()
        descripcion = self.desc_text.get(1.0, tk.END).strip()
        proveedor_id = self.proveedor_id.get()
        img_path = self.imagen_path.get()
        
        if not all([nombre, precio, stock, proveedor_id]):
            messagebox.showerror("Error", "Complete todos los campos obligatorios.")
            return
        
        try:
            precio_val = float(precio)
            stock_val = int(stock)
            prov_id_val = int(proveedor_id)
        except ValueError:
            messagebox.showerror("Error", "Precio, Stock y Proveedor ID deben ser números válidos.")
            return
        
        if self.product_id.get():
            # Actualizar
            query = """UPDATE Productos 
                       SET nombre=?, precio=?, stock=?, descripcion=?, proveedor_id=?, imagen_path=? 
                       WHERE id=?"""
            self.db.execute(
                query,
                (nombre, precio_val, stock_val, descripcion, prov_id_val, img_path, self.product_id.get())
            )
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
        else:
            # Insertar
            query = """INSERT INTO Productos 
                       (nombre, precio, stock, descripcion, proveedor_id, imagen_path) 
                       VALUES (?, ?, ?, ?, ?, ?)"""
            self.db.execute(
                query,
                (nombre, precio_val, stock_val, descripcion, prov_id_val, img_path)
            )
            messagebox.showinfo("Éxito", "Producto agregado correctamente.")
        
        self.load_products()
        self.reset_form()

    def delete_product(self):
        """Elimina el producto seleccionado."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un producto primero.")
            return
        
        prod_id = self.tree.item(selected_item, 'values')[0]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el producto ID {prod_id}?"):
            self.db.execute("DELETE FROM Productos WHERE id = ?", (prod_id,))
            messagebox.showinfo("Éxito", "Producto eliminado.")
            self.load_products()
            self.reset_form()

    def refresh_products(self):
        """Método público para refrescar la lista (usado por FileManager)."""
        self.load_products()