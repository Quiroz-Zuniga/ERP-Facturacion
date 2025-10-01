"""
file_manager.py - Gestor de Importación y Exportación
Maneja la importación/exportación de datos en formato CSV
"""

import csv
from tkinter import filedialog, messagebox, Toplevel
from tkinter import ttk
import tkinter as tk


class FileManager:
    """Maneja la importación y exportación de datos CSV."""

    TABLE_MAP = {
        "Productos": "Productos.csv",
        "Proveedores": "Proveedores.csv",
        "Usuarios": "Usuarios.csv",
        "Descuentos": "Descuentos.csv",
    }

    def __init__(self, db_manager):
        self.db = db_manager

    def get_data_from_db(self, table_name):
        """Obtiene datos de la DB para exportar."""
        if table_name == "Productos":
            return self.db.fetch(
                "SELECT id, nombre, descripcion, precio, stock, proveedor_id FROM Productos"
            )
        elif table_name == "Proveedores":
            return self.db.fetch(
                "SELECT id, nombre, contacto, telefono FROM Proveedores"
            )
        elif table_name == "Usuarios":
            return self.db.fetch("SELECT id, nombre, usuario, rol FROM Usuarios")
        elif table_name == "Descuentos":
            return self.db.fetch("SELECT id, nombre, tipo, porcentaje FROM Descuentos")
        return []

    def export_data(self, table_name):
        """Exporta datos a un archivo CSV."""
        data = self.get_data_from_db(table_name)

        if not data:
            messagebox.showinfo(
                "Exportar", f"No hay datos en {table_name} para exportar."
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=self.TABLE_MAP.get(table_name, "data.csv"),
            title=f"Guardar datos de {table_name}",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Escribir encabezados según la tabla
                headers = {
                    "Productos": [
                        "id",
                        "nombre",
                        "descripcion",
                        "precio",
                        "stock",
                        "proveedor_id",
                    ],
                    "Proveedores": ["id", "nombre", "contacto", "telefono"],
                    "Usuarios": ["id", "nombre", "usuario", "rol"],
                    "Descuentos": ["id", "nombre", "tipo", "porcentaje"],
                }

                writer.writerow(headers.get(table_name, []))
                writer.writerows(data)

            messagebox.showinfo("Éxito", f"Datos exportados a:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")

    def import_products(self, app_reference):
        """Importa productos desde un archivo CSV."""
        file_path = filedialog.askopenfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Seleccionar archivo CSV de Productos",
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)

                product_list = []
                for row in reader:
                    if len(row) >= 5:
                        # nombre, desc, precio, stock, prov_id
                        product_list.append(
                            (
                                row[1],  # nombre
                                row[2],  # descripcion
                                float(row[3]),  # precio
                                int(row[4]),  # stock
                                int(row[5]) if len(row) > 5 else 1,  # proveedor_id
                            )
                        )

            if product_list:
                self.show_import_preview(product_list, app_reference)
            else:
                messagebox.showwarning(
                    "Importar", "No se encontraron productos válidos en el archivo."
                )

        except Exception as e:
            messagebox.showerror(
                "Error de Importación",
                f"Error al leer el archivo.\n\nAsegúrese de que:\n"
                f"- El formato sea correcto (CSV)\n"
                f"- Precio y stock sean números válidos\n\n"
                f"Error: {e}",
            )

    def show_import_preview(self, product_list, app_reference):
        """Muestra vista previa de productos a importar."""
        preview_window = Toplevel()
        preview_window.title("Vista Previa de Importación")
        preview_window.geometry("800x500")

        # Encabezado
        ttk.Label(
            preview_window,
            text=f"Productos a importar: {len(product_list)}",
            font=("Arial", 14, "bold"),
        ).pack(pady=10)

        # Treeview con productos
        tree = ttk.Treeview(
            preview_window,
            columns=("Nombre", "Precio", "Stock", "Proveedor"),
            show="headings",
            height=15,
        )
        tree.heading("Nombre", text="Nombre")
        tree.heading("Precio", text="Precio")
        tree.heading("Stock", text="Stock")
        tree.heading("Proveedor", text="Proveedor ID")

        tree.column("Nombre", width=300)
        tree.column("Precio", width=100)
        tree.column("Stock", width=100)
        tree.column("Proveedor", width=100)

        tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Cargar datos
        for i, (nombre, desc, precio, stock, prov_id, img_path) in enumerate(
            product_list
        ):
            tree.insert(
                "",
                "end",
                iid=i,
                values=(nombre, f"${precio:.2f}", stock, prov_id),
                tags=(nombre, desc, precio, stock, prov_id, img_path),
            )

        def edit_selected():
            """Permite editar un producto antes de importar."""
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("Editar", "Seleccione un producto primero.")
                return

            data = tree.item(selected, "tags")

            edit_win = Toplevel(preview_window)
            edit_win.title("Editar Producto")
            edit_win.geometry("400x300")

            vars_list = [tk.StringVar(value=str(x)) for x in data]
            fields = [
                "Nombre",
                "Descripción",
                "Precio",
                "Stock",
                "Proveedor ID",
                "Imagen",
            ]

            for i, field in enumerate(fields):
                ttk.Label(edit_win, text=f"{field}:").grid(
                    row=i, column=0, padx=10, pady=5, sticky="w"
                )
                ttk.Entry(edit_win, textvariable=vars_list[i], width=30).grid(
                    row=i, column=1, padx=10, pady=5
                )

            def save_changes():
                try:
                    new_data = (
                        vars_list[0].get(),
                        vars_list[1].get(),
                        float(vars_list[2].get()),
                        int(vars_list[3].get()),
                        int(vars_list[4].get()),
                        vars_list[5].get(),
                    )
                    tree.item(selected, tags=new_data)
                    tree.item(
                        selected,
                        values=(
                            new_data[0],
                            f"${new_data[2]:.2f}",
                            new_data[3],
                            new_data[4],
                        ),
                    )
                    edit_win.destroy()
                except ValueError:
                    messagebox.showerror(
                        "Error", "Precio, Stock y Proveedor deben ser números."
                    )

            ttk.Button(edit_win, text="Guardar", command=save_changes).grid(
                row=len(fields), column=0, columnspan=2, pady=20
            )

        def confirm_import():
            """Guarda los productos en la base de datos."""
            final_products = []
            for item in tree.get_children():
                final_products.append(tree.item(item, "tags"))

            if not final_products:
                messagebox.showwarning("Importar", "No hay productos para importar.")
                return

            query = """INSERT INTO Productos 
                       (nombre, descripcion, precio, stock, proveedor_id) 
                       VALUES (?, ?, ?, ?, ?)"""

            try:
                self.db.cursor.executemany(query, final_products)
                self.db.conn.commit()
                messagebox.showinfo(
                    "Éxito", f"{len(final_products)} productos importados."
                )
                preview_window.destroy()

                # Refrescar la vista de productos si existe
                if hasattr(app_reference, "refresh_products"):
                    app_reference.refresh_products()

            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {e}")

        # Botones
        btn_frame = ttk.Frame(preview_window)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(btn_frame, text="Editar Seleccionado", command=edit_selected).pack(
            side="left", padx=5
        )
        ttk.Button(
            btn_frame, text="Confirmar Importación", command=confirm_import
        ).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=preview_window.destroy).pack(
            side="right", padx=5
        )
