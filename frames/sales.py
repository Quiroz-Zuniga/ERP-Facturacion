"""
frames/sales.py
Sistema POS (Point of Sale) para gestión de ventas
"""

from tkinter import ttk, messagebox, Toplevel, filedialog
import tkinter as tk
from datetime import datetime
import random
import os


class SalesFrame(ttk.Frame):
    """Frame de ventas POS."""

    def __init__(self, parent, app):
        super().__init__(parent, padding="10")
        self.app = app
        self.db = app.db
        self.cart = {}

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.cart_frame = ttk.Frame(self, padding="10", relief="groove")
        self.cart_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        self.checkout_frame = ttk.Frame(self, padding="15", relief="groove")
        self.checkout_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        self.create_cart_ui()
        self.create_checkout_ui()
        self.update_cart_display()

        # Atajos de teclado
        self.app.bind("<F1>", lambda e: self.open_product_search())
        self.app.bind("<F2>", lambda e: self.finalize_sale())

    def create_cart_ui(self):
        """Crea la interfaz del carrito."""
        ttk.Label(
            self.cart_frame, text="Carrito de Compras", font=("Arial", 14, "bold")
        ).pack(pady=(0, 10))

        ttk.Button(
            self.cart_frame,
            text="Buscar Producto (F1)",
            command=self.open_product_search,
        ).pack(fill="x", pady=5)

        # Treeview del carrito
        self.cart_tree = ttk.Treeview(
            self.cart_frame,
            columns=("ID", "Producto", "Cant", "PrecioU", "Desc", "Subtotal"),
            show="headings",
            height=15,
        )

        self.cart_tree.heading("ID", text="ID")
        self.cart_tree.heading("Producto", text="Producto")
        self.cart_tree.heading("Cant", text="Cant.")
        self.cart_tree.heading("PrecioU", text="P. Unit.")
        self.cart_tree.heading("Desc", text="Desc.")
        self.cart_tree.heading("Subtotal", text="Subtotal")

        self.cart_tree.column("ID", width=40, anchor="center")
        self.cart_tree.column("Producto", width=200)
        self.cart_tree.column("Cant", width=60, anchor="center")
        self.cart_tree.column("PrecioU", width=80, anchor="center")
        self.cart_tree.column("Desc", width=60, anchor="center")
        self.cart_tree.column("Subtotal", width=90, anchor="center")

        self.cart_tree.pack(fill="both", expand=True, pady=10)

        # Botones de acción
        action_frame = ttk.Frame(self.cart_frame)
        action_frame.pack(fill="x", pady=5)

        ttk.Button(
            action_frame, text="Eliminar Producto", command=self.remove_from_cart
        ).pack(side="left", padx=5)

        ttk.Button(
            action_frame, text="Aplicar Descuento", command=self.apply_discount
        ).pack(side="left", padx=5)

        ttk.Button(action_frame, text="Limpiar Carrito", command=self.clear_cart).pack(
            side="right", padx=5
        )

    def create_checkout_ui(self):
        """Crea la interfaz de pago."""
        ttk.Label(
            self.checkout_frame, text="Resumen de Venta", font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))

        # Variables
        self.total_var = tk.DoubleVar(value=0.0)
        self.monto_pagado_var = tk.DoubleVar(value=0.0)
        self.vuelto_var = tk.DoubleVar(value=0.0)

        # Total
        ttk.Label(self.checkout_frame, text="TOTAL A PAGAR:", font=("Arial", 14)).pack(
            anchor="w"
        )

        total_label = ttk.Label(
            self.checkout_frame,
            textvariable=self.total_var,
            font=("Arial", 32, "bold"),
            foreground="#dc3545",
        )
        total_label.pack(anchor="w", pady=(5, 20))

        # Frame de monto recibido
        monto_frame = ttk.Frame(self.checkout_frame)
        monto_frame.pack(fill="x", pady=10)

        ttk.Label(monto_frame, text="Monto Recibido:", font=("Arial", 12)).pack(
            side="left", padx=5
        )

        self.monto_entry = ttk.Entry(
            monto_frame,
            textvariable=self.monto_pagado_var,
            font=("Arial", 14),
            width=15,
        )
        self.monto_entry.pack(side="left", expand=True, fill="x")
        self.monto_entry.bind("<KeyRelease>", self.calculate_change)

        # Vuelto
        ttk.Label(self.checkout_frame, text="VUELTO:", font=("Arial", 14)).pack(
            anchor="w", pady=(20, 0)
        )

        vuelto_label = ttk.Label(
            self.checkout_frame,
            textvariable=self.vuelto_var,
            font=("Arial", 28, "bold"),
            foreground="#28a745",
        )
        vuelto_label.pack(anchor="w", pady=(5, 20))

        # Botón de pago
        ttk.Button(
            self.checkout_frame, text="FINALIZAR VENTA (F2)", command=self.finalize_sale
        ).pack(fill="x", pady=20)

        # Estado
        self.status_label = ttk.Label(
            self.checkout_frame,
            text="Agregue productos al carrito",
            font=("Arial", 10),
            foreground="#666",
        )
        self.status_label.pack(pady=10)

    def open_product_search(self):
        """Abre ventana de búsqueda de productos."""
        search_win = Toplevel(self.app)
        search_win.title("Buscar Productos")
        search_win.geometry("900x600")

        search_win.grid_columnconfigure(0, weight=2)
        search_win.grid_columnconfigure(1, weight=1)
        search_win.grid_rowconfigure(2, weight=1)

        ttk.Label(
            search_win, text="Búsqueda de Productos", font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Búsqueda
        search_frame = ttk.Frame(search_win)
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        search_var = tk.StringVar()
        ttk.Label(search_frame, text="Buscar:").pack(side="left", padx=5)
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.bind(
            "<KeyRelease>", lambda e: self.filter_search(tree, search_var.get())
        )

        # Treeview de productos
        tree = ttk.Treeview(
            search_win,
            columns=("ID", "Nombre", "Stock", "Precio"),
            show="headings",
            height=15,
        )

        tree.heading("ID", text="ID")
        tree.heading("Nombre", text="Producto")
        tree.heading("Stock", text="Stock")
        tree.heading("Precio", text="Precio")

        tree.column("ID", width=50, anchor="center")
        tree.column("Nombre", width=300)
        tree.column("Stock", width=80, anchor="center")
        tree.column("Precio", width=100, anchor="center")

        tree.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        tree.bind(
            "<<TreeviewSelect>>", lambda e: self.show_product_detail(tree, detail_frame)
        )

        # Panel de detalle
        detail_frame = ttk.LabelFrame(
            search_win, text="Detalle del Producto", padding=10
        )
        detail_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)

        self.detail_label = ttk.Label(
            detail_frame, text="Seleccione un producto", justify=tk.LEFT, wraplength=200
        )
        self.detail_label.pack(fill="both", expand=True)

        # Cantidad y botón
        qty_frame = ttk.Frame(detail_frame)
        qty_frame.pack(fill="x", pady=10)

        qty_var = tk.IntVar(value=1)
        ttk.Label(qty_frame, text="Cantidad:").pack(side="left", padx=5)
        ttk.Spinbox(qty_frame, from_=1, to=100, textvariable=qty_var, width=10).pack(
            side="left", padx=5
        )

        ttk.Button(
            detail_frame,
            text="Añadir al Carrito",
            command=lambda: self.add_from_search(tree, qty_var.get(), search_win),
        ).pack(fill="x", pady=5)

        # Cargar productos
        self.load_products_search(tree)

    def load_products_search(self, tree):
        """Carga productos en la ventana de búsqueda."""
        for item in tree.get_children():
            tree.delete(item)

        products = self.db.fetch(
            "SELECT id, nombre, stock, precio, descripcion FROM Productos WHERE stock > 0"
        )

        for prod in products:
            tree.insert(
                "",
                "end",
                values=(prod[0], prod[1], prod[2], f"${prod[3]:.2f}"),
                tags=(prod,),
            )

    def filter_search(self, tree, search_term):
        """Filtra productos en búsqueda."""
        for item in tree.get_children():
            tree.delete(item)

        if not search_term:
            self.load_products_search(tree)
            return

        products = self.db.fetch(
            "SELECT id, nombre, stock, precio, descripcion FROM Productos WHERE stock > 0"
        )

        search_lower = search_term.lower()
        for prod in products:
            if search_lower in prod[1].lower():
                tree.insert(
                    "",
                    "end",
                    values=(prod[0], prod[1], prod[2], f"${prod[3]:.2f}"),
                    tags=(prod,),
                )

    def show_product_detail(self, tree, detail_frame):
        """Muestra detalle del producto seleccionado."""
        selected = tree.focus()
        if not selected:
            return

        try:
            # Obtener los valores directamente de la vista, que son más confiables
            values = tree.item(selected, "values")

            if not values or len(values) < 4:
                self.detail_label.config(
                    text="Error: No se pudieron cargar los datos del producto"
                )
                return

            # values = (id, nombre, stock, precio_formateado)
            nombre = values[1]
            stock = values[2]
            # Limpiar el formato del precio ($20.00 -> 20.00)
            precio_str = values[3].replace("$", "").replace(",", "")
            precio = float(precio_str)

            # Para la descripción, buscarla en la base de datos
            prod_id = values[0]
            result = self.db.fetch(
                "SELECT descripcion FROM Productos WHERE id = ?", (prod_id,)
            )
            desc = result[0][0] if result and result[0] else "Sin descripción"

            detail_text = f"Nombre: {nombre}\n\n"
            detail_text += f"Stock: {stock} unidades\n\n"
            detail_text += f"Precio: ${precio:.2f}\n\n"
            detail_text += f"Descripción:\n{desc or 'Sin descripción'}"

            self.detail_label.config(text=detail_text)

        except (ValueError, IndexError, TypeError) as e:
            self.detail_label.config(text=f"Error al cargar datos del producto: {e}")

    def add_from_search(self, tree, quantity, window):
        """Añade producto al carrito desde búsqueda."""
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return

        if quantity <= 0:
            messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
            return

        try:
            # Obtener los valores directamente de la vista, que son más confiables
            item_values = tree.item(selected, "values")

            if not item_values or len(item_values) < 4:
                messagebox.showerror("Error", "No se encontraron datos del producto")
                return

            # values = (id, nombre, stock, precio_formateado)
            prod_id = int(item_values[0])
            nombre = str(item_values[1])
            stock = int(item_values[2])
            # Limpiar el formato del precio ($20.00 -> 20.00)
            precio_str = item_values[3].replace("$", "").replace(",", "")
            precio = float(precio_str)

            current_qty = self.cart.get(prod_id, {}).get("cantidad", 0)
            if (current_qty + quantity) > stock:
                messagebox.showerror(
                    "Stock Insuficiente", f"Solo hay {stock} unidades disponibles"
                )
                return

            if prod_id in self.cart:
                self.cart[prod_id]["cantidad"] += quantity
            else:
                self.cart[prod_id] = {
                    "id": prod_id,
                    "nombre": nombre,
                    "precio_unitario": precio,
                    "cantidad": quantity,
                    "descuento_porcentaje": 0.0,
                }

            self.update_cart_display()
            messagebox.showinfo("Éxito", f"{nombre} añadido al carrito")
            window.destroy()

        except (IndexError, ValueError, TypeError) as e:
            error_msg = f"Error al obtener datos del producto: {e}"
            if "item_values" in locals():
                error_msg += f"\nValues: {item_values}"
            error_msg += "\nIntente seleccionar el producto nuevamente."
            messagebox.showerror("Error", error_msg)

    def update_cart_display(self):
        """Actualiza la visualización del carrito."""
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total = 0.0
        for prod_id, data in self.cart.items():
            cant = data["cantidad"]
            precio = data["precio_unitario"]
            desc_pct = data["descuento_porcentaje"]

            desc_monto = (precio * cant) * desc_pct
            subtotal = (precio * cant) - desc_monto
            total += subtotal

            self.cart_tree.insert(
                "",
                "end",
                iid=prod_id,
                values=(
                    prod_id,
                    data["nombre"],
                    cant,
                    f"${precio:.2f}",
                    f"{int(desc_pct*100)}%",
                    f"${subtotal:.2f}",
                ),
            )

        self.total_var.set(round(total, 2))
        self.calculate_change()

    def calculate_change(self, event=None):
        """Calcula el vuelto."""
        try:
            total = self.total_var.get()
            pagado = self.monto_pagado_var.get()
            vuelto = pagado - total

            self.vuelto_var.set(round(max(0, vuelto), 2))

            if vuelto < 0:
                self.status_label.config(
                    text=f"Falta: ${abs(vuelto):.2f}", foreground="#dc3545"
                )
            else:
                self.status_label.config(
                    text="Listo para procesar", foreground="#28a745"
                )
        except:
            self.vuelto_var.set(0.0)

    def remove_from_cart(self):
        """Elimina producto del carrito."""
        selected = self.cart_tree.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return

        try:
            # Convertir a entero para que coincida con las claves del carrito
            prod_id = int(self.cart_tree.item(selected, "values")[0])
            if prod_id in self.cart:
                del self.cart[prod_id]
                self.update_cart_display()
            else:
                messagebox.showerror("Error", "Producto no encontrado en el carrito")
        except (ValueError, IndexError) as e:
            messagebox.showerror("Error", f"Error al eliminar producto: {e}")

    def clear_cart(self):
        """Limpia todo el carrito."""
        if not self.cart:
            return

        if messagebox.askyesno("Confirmar", "¿Limpiar todo el carrito?"):
            self.cart = {}
            self.update_cart_display()
            self.monto_pagado_var.set(0.0)

    def apply_discount(self):
        """Aplica descuento a producto seleccionado."""
        selected = self.cart_tree.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return

        try:
            # Convertir a entero para que coincida con las claves del carrito
            prod_id = int(self.cart_tree.item(selected, "values")[0])

            if prod_id not in self.cart:
                messagebox.showerror("Error", "Producto no encontrado en el carrito")
                return

        except (ValueError, IndexError) as e:
            messagebox.showerror("Error", f"Error al obtener datos del producto: {e}")
            return

        # Ventana de descuento
        disc_win = Toplevel(self.app)
        disc_win.title("Aplicar Descuento")
        disc_win.geometry("300x200")

        ttk.Label(disc_win, text="Descuento (%):").pack(pady=10)

        disc_var = tk.StringVar(value="0")
        ttk.Entry(disc_win, textvariable=disc_var, width=20).pack(pady=5)

        def apply():
            try:
                pct = float(disc_var.get()) / 100.0
                if pct < 0 or pct >= 1:
                    messagebox.showerror("Error", "Porcentaje debe estar entre 0 y 99")
                    return

                self.cart[prod_id]["descuento_porcentaje"] = pct
                self.update_cart_display()
                disc_win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un número válido")

        ttk.Button(disc_win, text="Aplicar", command=apply).pack(pady=20)

    def finalize_sale(self):
        """Finaliza la venta y genera recibo."""
        if not self.cart:
            messagebox.showwarning("Advertencia", "El carrito está vacío")
            return

        total = self.total_var.get()
        pagado = self.monto_pagado_var.get()

        if pagado < total:
            messagebox.showerror("Error", "Monto insuficiente")
            return

        vuelto = self.vuelto_var.get()
        venta_id = (
            f"V-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}"
        )
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # Guardar venta
            self.db.execute(
                "INSERT INTO Ventas (id, fecha, total, monto_pagado, vuelto, usuario_id, tipo_recibo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    venta_id,
                    fecha,
                    total,
                    pagado,
                    vuelto,
                    self.app.current_user[0],
                    "HTML",
                ),
            )

            # Guardar detalle y actualizar stock
            for prod_id, data in self.cart.items():
                cant = data["cantidad"]
                precio = data["precio_unitario"]
                desc_pct = data["descuento_porcentaje"]
                desc_monto = (precio * cant) * desc_pct
                subtotal = (precio * cant) - desc_monto

                self.db.execute(
                    "INSERT INTO DetalleVenta (venta_id, producto_id, nombre_producto, cantidad, precio_unitario, descuento, subtotal) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        venta_id,
                        prod_id,
                        data["nombre"],
                        cant,
                        precio,
                        desc_monto,
                        subtotal,
                    ),
                )

                self.db.execute(
                    "UPDATE Productos SET stock = stock - ? WHERE id = ?",
                    (cant, prod_id),
                )

            # Generar recibo
            self.generate_receipt(venta_id, total, pagado, vuelto, fecha)

            messagebox.showinfo("Éxito", f"Venta {venta_id} procesada correctamente")

            self.cart = {}
            self.update_cart_display()
            self.monto_pagado_var.set(0.0)

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar venta: {e}")

    def generate_receipt(self, venta_id, total, pagado, vuelto, fecha):
        """Genera el recibo HTML."""
        template = self.db.get_config(
            "recibo_template", self.db.default_receipt_template()
        )

        items_html = ""
        for data in self.cart.values():
            cant = data["cantidad"]
            precio = data["precio_unitario"]
            desc_pct = data["descuento_porcentaje"]
            desc_monto = (precio * cant) * desc_pct
            subtotal = (precio * cant) - desc_monto

            desc_text = f" (-{int(desc_pct*100)}%)" if desc_pct > 0 else ""
            items_html += f'<div class="item"><span>{data["nombre"]}{desc_text}</span><span>{cant} / ${subtotal:.2f}</span></div>\n'

        html_content = template
        html_content = html_content.replace("{{NOMBRE_NEGOCIO}}", "Mi Negocio ERP")
        html_content = html_content.replace("{{ID_VENTA}}", venta_id)
        html_content = html_content.replace("{{FECHA}}", fecha)
        html_content = html_content.replace("{{TOTAL}}", f"{total:.2f}")
        html_content = html_content.replace("{{MONTO_PAGADO}}", f"{pagado:.2f}")
        html_content = html_content.replace("{{VUELTO}}", f"{vuelto:.2f}")
        html_content = html_content.replace("<!-- ITEMS_PLACEHOLDER -->", items_html)

        # Guardar recibo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML", "*.html")],
            initialfile=f"Recibo_{venta_id}.html",
        )

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            messagebox.showinfo("Recibo", f"Recibo guardado en:\n{file_path}")
