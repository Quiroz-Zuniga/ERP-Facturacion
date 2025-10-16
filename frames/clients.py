"""
frames/clients.py - Módulo de Gestión de Clientes
Maneja el registro, edición, eliminación y consulta de clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from datetime import datetime
import csv
import re


class ClientsFrame(ttk.Frame):
    """Frame para gestión completa de clientes."""

    def __init__(self, parent, app):
        super().__init__(parent, padding="10")
        self.app = app
        self.db = app.db
        self.setup_ui()
        self.load_clients()

    def setup_ui(self):
        """Configura la interfaz de usuario."""

        # Título principal
        title_label = ttk.Label(
            self, text="GESTIÓN DE CLIENTES", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Frame principal con dos columnas
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ============ COLUMNA IZQUIERDA - FORMULARIO ============
        left_frame = ttk.LabelFrame(
            main_frame, text="Información del Cliente", padding=15
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Variables del formulario
        self.nombre_var = tk.StringVar()
        self.apellido_var = tk.StringVar()
        self.dni_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        self.activo_var = tk.BooleanVar(value=True)
        self.cliente_id_seleccionado = None

        # Nombre
        ttk.Label(left_frame, text="Nombre *:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.nombre_entry = ttk.Entry(
            left_frame, textvariable=self.nombre_var, width=30
        )
        self.nombre_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5)

        # Apellido
        ttk.Label(left_frame, text="Apellido *:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.apellido_entry = ttk.Entry(
            left_frame, textvariable=self.apellido_var, width=30
        )
        self.apellido_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=5)

        # DNI/Identidad
        ttk.Label(left_frame, text="DNI/Identidad:").grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.dni_entry = ttk.Entry(left_frame, textvariable=self.dni_var, width=30)
        self.dni_entry.grid(row=2, column=1, columnspan=2, sticky="ew", pady=5)

        # Teléfono
        ttk.Label(left_frame, text="Teléfono:").grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.telefono_entry = ttk.Entry(
            left_frame, textvariable=self.telefono_var, width=30
        )
        self.telefono_entry.grid(row=3, column=1, columnspan=2, sticky="ew", pady=5)

        # Email
        ttk.Label(left_frame, text="Email:").grid(row=4, column=0, sticky="w", pady=5)
        self.email_entry = ttk.Entry(left_frame, textvariable=self.email_var, width=30)
        self.email_entry.grid(row=4, column=1, columnspan=2, sticky="ew", pady=5)

        # Dirección
        ttk.Label(left_frame, text="Dirección:").grid(
            row=5, column=0, sticky="w", pady=5
        )
        self.direccion_text = tk.Text(left_frame, height=3, width=30)
        self.direccion_text.grid(row=5, column=1, columnspan=2, sticky="ew", pady=5)

        # Estado activo
        self.activo_check = ttk.Checkbutton(
            left_frame, text="Cliente Activo", variable=self.activo_var
        )
        self.activo_check.grid(row=6, column=1, sticky="w", pady=10)

        # Botones de acción
        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.grid(row=7, column=0, columnspan=3, pady=15, sticky="ew")

        ttk.Button(
            buttons_frame,
            text="💾 Guardar",
            command=self.save_client,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="✏️ Editar", command=self.edit_client).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="🗑️ Eliminar", command=self.delete_client).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(buttons_frame, text="🔄 Limpiar", command=self.clear_form).pack(
            side=tk.LEFT, padx=5
        )

        # Configurar expansión de columnas
        left_frame.columnconfigure(1, weight=1)

        # ============ COLUMNA DERECHA - LISTA Y CONTROLES ============
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Marco de búsqueda
        search_frame = ttk.LabelFrame(right_frame, text="Búsqueda", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_clients)
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Filtro por estado
        self.filter_var = tk.StringVar(value="todos")
        filter_frame = ttk.Frame(search_frame)
        filter_frame.pack(side=tk.RIGHT, padx=10)
        ttk.Label(filter_frame, text="Estado:").pack(side=tk.LEFT)
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["todos", "activos", "inactivos"],
            state="readonly",
            width=10,
        )
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_clients())

        # Lista de clientes
        list_frame = ttk.LabelFrame(right_frame, text="Lista de Clientes", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar Treeview
        columns = ("ID", "Nombre", "Apellido", "DNI", "Teléfono", "Email", "Estado")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=12
        )

        # Configurar encabezados
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Apellido", text="Apellido")
        self.tree.heading("DNI", text="DNI")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Estado", text="Estado")

        # Configurar anchos de columna
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=120)
        self.tree.column("Apellido", width=120)
        self.tree.column("DNI", width=100)
        self.tree.column("Teléfono", width=100)
        self.tree.column("Email", width=150)
        self.tree.column("Estado", width=80)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set
        )

        # Empaquetar tree y scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Eventos del tree
        self.tree.bind("<<TreeviewSelect>>", self.on_client_select)
        self.tree.bind("<Double-1>", lambda e: self.edit_client())

        # Botones de exportación/importación
        export_frame = ttk.Frame(right_frame)
        export_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            export_frame, text="📤 Exportar CSV", command=self.export_to_csv
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            export_frame, text="📥 Importar CSV", command=self.import_from_csv
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            export_frame, text="📊 Estadísticas", command=self.show_statistics
        ).pack(side=tk.RIGHT, padx=5)

    def load_clients(self):
        """Carga la lista de clientes desde la base de datos."""
        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Construir consulta según filtro
        filter_estado = self.filter_var.get()
        if filter_estado == "activos":
            query = "SELECT * FROM Clientes WHERE activo = 1 ORDER BY apellido, nombre"
        elif filter_estado == "inactivos":
            query = "SELECT * FROM Clientes WHERE activo = 0 ORDER BY apellido, nombre"
        else:
            query = "SELECT * FROM Clientes ORDER BY apellido, nombre"

        clientes = self.db.fetch(query)

        for cliente in clientes:
            (
                id_cliente,
                nombre,
                apellido,
                dni,
                telefono,
                email,
                direccion,
                fecha_registro,
                activo,
            ) = cliente
            estado = "Activo" if activo else "Inactivo"

            # Insertar en el tree con tags según estado
            tag = "activo" if activo else "inactivo"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    id_cliente,
                    nombre,
                    apellido,
                    dni or "N/A",
                    telefono or "N/A",
                    email or "N/A",
                    estado,
                ),
                tags=(tag,),
            )

        # Configurar colores según estado
        self.tree.tag_configure("activo", foreground="black")
        self.tree.tag_configure("inactivo", foreground="gray")

    def search_clients(self, *args):
        """Busca clientes en tiempo real."""
        search_term = self.search_var.get().lower()

        # Limpiar lista actual
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not search_term:
            self.load_clients()
            return

        # Buscar en nombre, apellido, DNI, teléfono y email
        query = """
            SELECT * FROM Clientes 
            WHERE LOWER(nombre) LIKE ? 
            OR LOWER(apellido) LIKE ? 
            OR LOWER(dni) LIKE ? 
            OR LOWER(telefono) LIKE ? 
            OR LOWER(email) LIKE ?
            ORDER BY apellido, nombre
        """
        search_pattern = f"%{search_term}%"
        clientes = self.db.fetch(
            query,
            (
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
            ),
        )

        for cliente in clientes:
            (
                id_cliente,
                nombre,
                apellido,
                dni,
                telefono,
                email,
                direccion,
                fecha_registro,
                activo,
            ) = cliente
            estado = "Activo" if activo else "Inactivo"
            tag = "activo" if activo else "inactivo"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    id_cliente,
                    nombre,
                    apellido,
                    dni or "N/A",
                    telefono or "N/A",
                    email or "N/A",
                    estado,
                ),
                tags=(tag,),
            )

        # Aplicar colores
        self.tree.tag_configure("activo", foreground="black")
        self.tree.tag_configure("inactivo", foreground="gray")

    def on_client_select(self, event):
        """Maneja la selección de un cliente en la lista."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item["values"]
            if values:
                self.cliente_id_seleccionado = values[0]
                # Cargar datos completos del cliente
                self.load_client_details(self.cliente_id_seleccionado)

    def load_client_details(self, cliente_id):
        """Carga los detalles completos de un cliente en el formulario."""
        cliente = self.db.fetch("SELECT * FROM Clientes WHERE id = ?", (cliente_id,))
        if cliente:
            cliente_data = cliente[0]
            (
                id_cliente,
                nombre,
                apellido,
                dni,
                telefono,
                email,
                direccion,
                fecha_registro,
                activo,
            ) = cliente_data

            # Llenar formulario
            self.nombre_var.set(nombre)
            self.apellido_var.set(apellido)
            self.dni_var.set(dni or "")
            self.telefono_var.set(telefono or "")
            self.email_var.set(email or "")
            self.direccion_text.delete("1.0", tk.END)
            self.direccion_text.insert("1.0", direccion or "")
            self.activo_var.set(bool(activo))

    def validate_form(self):
        """Valida los datos del formulario."""
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            self.nombre_entry.focus()
            return False

        if not self.apellido_var.get().strip():
            messagebox.showerror("Error", "El apellido es obligatorio")
            self.apellido_entry.focus()
            return False

        # Validar DNI si se proporciona
        dni = self.dni_var.get().strip()
        if dni and not re.match(r"^[0-9]{13}$", dni):
            messagebox.showerror("Error", "El DNI debe tener 13 dígitos")
            self.dni_entry.focus()
            return False

        # Validar email si se proporciona
        email = self.email_var.get().strip()
        if email and not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            messagebox.showerror("Error", "Formato de email inválido")
            self.email_entry.focus()
            return False

        return True

    def save_client(self):
        """Guarda un nuevo cliente o actualiza uno existente."""
        if not self.validate_form():
            return

        nombre = self.nombre_var.get().strip()
        apellido = self.apellido_var.get().strip()
        dni = self.dni_var.get().strip() or None
        telefono = self.telefono_var.get().strip() or None
        email = self.email_var.get().strip() or None
        direccion = self.direccion_text.get("1.0", tk.END).strip() or None
        activo = 1 if self.activo_var.get() else 0

        try:
            if self.cliente_id_seleccionado:
                # Actualizar cliente existente
                query = """
                    UPDATE Clientes 
                    SET nombre=?, apellido=?, dni=?, telefono=?, email=?, direccion=?, activo=?
                    WHERE id=?
                """
                self.db.execute(
                    query,
                    (
                        nombre,
                        apellido,
                        dni,
                        telefono,
                        email,
                        direccion,
                        activo,
                        self.cliente_id_seleccionado,
                    ),
                )
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
            else:
                # Crear nuevo cliente
                fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                query = """
                    INSERT INTO Clientes (nombre, apellido, dni, telefono, email, direccion, fecha_registro, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.db.execute(
                    query,
                    (
                        nombre,
                        apellido,
                        dni,
                        telefono,
                        email,
                        direccion,
                        fecha_registro,
                        activo,
                    ),
                )
                messagebox.showinfo("Éxito", "Cliente registrado correctamente")

            self.clear_form()
            self.load_clients()

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror(
                    "Error", "El DNI ya está registrado para otro cliente"
                )
            else:
                messagebox.showerror("Error", f"Error al guardar cliente: {e}")

    def edit_client(self):
        """Prepara la edición del cliente seleccionado."""
        if not self.cliente_id_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar")
            return

        # Los datos ya están cargados en el formulario por on_client_select
        messagebox.showinfo(
            "Modo Edición",
            "Modifique los campos y presione 'Guardar' para confirmar los cambios",
        )

    def delete_client(self):
        """Elimina el cliente seleccionado."""
        if not self.cliente_id_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return

        # Verificar si el cliente tiene ventas asociadas
        ventas = self.db.fetch(
            "SELECT COUNT(*) FROM Ventas WHERE cliente_id = ?",
            (self.cliente_id_seleccionado,),
        )
        tiene_ventas = ventas[0][0] > 0 if ventas else False

        if tiene_ventas:
            respuesta = messagebox.askyesno(
                "Cliente con Ventas",
                "Este cliente tiene ventas registradas.\n¿Desea desactivarlo en lugar de eliminarlo?\n\n"
                "Sí = Desactivar (recomendado)\nNo = Eliminar permanentemente",
            )
            if respuesta:
                # Desactivar cliente
                self.db.execute(
                    "UPDATE Clientes SET activo = 0 WHERE id = ?",
                    (self.cliente_id_seleccionado,),
                )
                messagebox.showinfo("Éxito", "Cliente desactivado correctamente")
            else:
                # Confirmar eliminación definitiva
                if messagebox.askyesno(
                    "Confirmación",
                    "⚠️ ADVERTENCIA: Se eliminarán también todas las ventas asociadas.\n¿Continuar?",
                ):
                    self.db.execute(
                        "DELETE FROM DetalleVenta WHERE venta_id IN (SELECT id FROM Ventas WHERE cliente_id = ?)",
                        (self.cliente_id_seleccionado,),
                    )
                    self.db.execute(
                        "DELETE FROM Ventas WHERE cliente_id = ?",
                        (self.cliente_id_seleccionado,),
                    )
                    self.db.execute(
                        "DELETE FROM Clientes WHERE id = ?",
                        (self.cliente_id_seleccionado,),
                    )
                    messagebox.showinfo(
                        "Éxito", "Cliente y ventas asociadas eliminados"
                    )
        else:
            # Cliente sin ventas, eliminación simple
            if messagebox.askyesno(
                "Confirmación", "¿Está seguro de eliminar este cliente?"
            ):
                self.db.execute(
                    "DELETE FROM Clientes WHERE id = ?", (self.cliente_id_seleccionado,)
                )
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")

        self.clear_form()
        self.load_clients()

    def clear_form(self):
        """Limpia el formulario."""
        self.nombre_var.set("")
        self.apellido_var.set("")
        self.dni_var.set("")
        self.telefono_var.set("")
        self.email_var.set("")
        self.direccion_text.delete("1.0", tk.END)
        self.activo_var.set(True)
        self.cliente_id_seleccionado = None

        # Limpiar selección en la lista
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def export_to_csv(self):
        """Exporta la lista de clientes a CSV."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Exportar Clientes",
        )

        if filename:
            try:
                clientes = self.db.fetch(
                    "SELECT * FROM Clientes ORDER BY apellido, nombre"
                )

                with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    # Encabezados
                    writer.writerow(
                        [
                            "ID",
                            "Nombre",
                            "Apellido",
                            "DNI",
                            "Teléfono",
                            "Email",
                            "Dirección",
                            "Fecha Registro",
                            "Activo",
                        ]
                    )

                    # Datos
                    for cliente in clientes:
                        writer.writerow(cliente)

                messagebox.showinfo("Éxito", f"Clientes exportados a {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {e}")

    def import_from_csv(self):
        """Importa clientes desde un archivo CSV."""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Importar Clientes",
        )

        if filename:
            try:
                imported_count = 0
                skipped_count = 0

                with open(filename, "r", encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)

                    for row in reader:
                        try:
                            # Validar campos obligatorios
                            if not row.get("Nombre") or not row.get("Apellido"):
                                skipped_count += 1
                                continue

                            fecha_registro = datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )

                            query = """
                                INSERT INTO Clientes (nombre, apellido, dni, telefono, email, direccion, fecha_registro, activo)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """
                            self.db.execute(
                                query,
                                (
                                    row["Nombre"],
                                    row["Apellido"],
                                    row.get("DNI") or None,
                                    row.get("Teléfono") or None,
                                    row.get("Email") or None,
                                    row.get("Dirección") or None,
                                    fecha_registro,
                                    1 if row.get("Activo", "1") == "1" else 0,
                                ),
                            )
                            imported_count += 1

                        except Exception as e:
                            if "UNIQUE constraint failed" not in str(e):
                                skipped_count += 1

                self.load_clients()
                messagebox.showinfo(
                    "Importación Completa",
                    f"Clientes importados: {imported_count}\nRegistros omitidos: {skipped_count}",
                )

            except Exception as e:
                messagebox.showerror("Error", f"Error al importar: {e}")

    def show_statistics(self):
        """Muestra estadísticas de clientes."""
        try:
            total_clientes = self.db.fetch("SELECT COUNT(*) FROM Clientes")[0][0]
            clientes_activos = self.db.fetch(
                "SELECT COUNT(*) FROM Clientes WHERE activo = 1"
            )[0][0]
            clientes_inactivos = total_clientes - clientes_activos

            # Clientes con ventas
            clientes_con_ventas = self.db.fetch(
                "SELECT COUNT(DISTINCT cliente_id) FROM Ventas WHERE cliente_id IS NOT NULL"
            )[0][0]

            # Clientes registrados este mes
            fecha_inicio_mes = datetime.now().strftime("%Y-%m-01")
            clientes_este_mes = self.db.fetch(
                "SELECT COUNT(*) FROM Clientes WHERE fecha_registro >= ?",
                (fecha_inicio_mes,),
            )[0][0]

            stats_text = f"""
📊 ESTADÍSTICAS DE CLIENTES

👥 Total de clientes: {total_clientes}
✅ Clientes activos: {clientes_activos}
❌ Clientes inactivos: {clientes_inactivos}
🛒 Clientes con ventas: {clientes_con_ventas}
📅 Registrados este mes: {clientes_este_mes}

💼 Porcentaje de actividad: {(clientes_activos/total_clientes*100):.1f}% (activos)
🛍️ Porcentaje con compras: {(clientes_con_ventas/total_clientes*100):.1f}% (compradores)
            """.strip()

            messagebox.showinfo("Estadísticas de Clientes", stats_text)

        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular estadísticas: {e}")
