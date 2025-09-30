"""
database.py - Gestor de Base de Datos SQLite
Maneja todas las operaciones CRUD y estructura de la base de datos
"""
import sqlite3
from tkinter import messagebox


class DBManager:
    """Maneja la conexión a SQLite y operaciones CRUD/Setup."""
    
    def __init__(self, db_name="erp_profesional.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Crea todas las tablas necesarias del sistema."""
        
        # Tabla de Productos
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL,
                proveedor_id INTEGER,
                imagen_path TEXT,
                FOREIGN KEY (proveedor_id) REFERENCES Proveedores(id)
            )
        """)
        
        # Tabla de Proveedores
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                contacto TEXT,
                telefono TEXT
            )
        """)
        
        # Tabla de Usuarios
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL,
                rol TEXT NOT NULL
            )
        """)
        
        # Tabla de Descuentos
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Descuentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT,
                porcentaje REAL NOT NULL
            )
        """)
        
        # Tabla de Configuración
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
        """)
        
        # Tabla de Ventas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Ventas (
                id TEXT PRIMARY KEY,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                monto_pagado REAL,
                vuelto REAL,
                usuario_id INTEGER,
                tipo_recibo TEXT
            )
        """)
        
        # Tabla de Detalle de Venta
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS DetalleVenta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id TEXT,
                producto_id INTEGER,
                nombre_producto TEXT,
                cantidad INTEGER,
                precio_unitario REAL,
                descuento REAL DEFAULT 0,
                subtotal REAL,
                FOREIGN KEY (venta_id) REFERENCES Ventas(id)
            )
        """)
        
        self.conn.commit()
        self.insert_initial_data()

    def insert_initial_data(self):
        """Inserta datos iniciales si las tablas están vacías."""
        
        # Usuario administrador por defecto
        if not self.fetch("SELECT * FROM Usuarios"):
            self.execute(
                "INSERT INTO Usuarios (nombre, usuario, contrasena, rol) VALUES (?, ?, ?, ?)",
                ('Administrador', 'admin', '1234', 'Administrador')
            )
        
        # Proveedor de ejemplo
        if not self.fetch("SELECT * FROM Proveedores"):
            self.execute(
                "INSERT INTO Proveedores (nombre, contacto, telefono) VALUES (?, ?, ?)",
                ('Distribuidora Central', 'Juan Pérez', '555-1234')
            )
        
        # Descuentos predefinidos
        if not self.fetch("SELECT * FROM Descuentos"):
            self.execute(
                "INSERT INTO Descuentos (nombre, tipo, porcentaje) VALUES (?, ?, ?)",
                ('Docena 10%', 'Docena', 0.10)
            )
            self.execute(
                "INSERT INTO Descuentos (nombre, tipo, porcentaje) VALUES (?, ?, ?)",
                ('Mayorista 15%', 'Mayorista', 0.15)
            )
        
        # Plantilla de recibo por defecto
        if not self.fetch("SELECT * FROM Configuracion WHERE clave = 'recibo_template'"):
            self.set_config('recibo_template', self.default_receipt_template())
        
        # Productos de ejemplo
        if not self.fetch("SELECT * FROM Productos"):
            productos_ejemplo = [
                ('Monitor 27"', 'Monitor 4K profesional', 320.00, 15, 1, 'monitor.png'),
                ('Teclado Mecánico', 'Switches Blue, RGB', 45.00, 105, 1, 'teclado.png'),
                ('Mouse Gamer', 'RGB, 16000 DPI', 35.00, 50, 1, 'mouse.png'),
                ('Laptop HP', 'i5, 8GB RAM, 256GB SSD', 650.00, 8, 1, 'laptop.png'),
            ]
            self.cursor.executemany(
                "INSERT INTO Productos (nombre, descripcion, precio, stock, proveedor_id, imagen_path) VALUES (?, ?, ?, ?, ?, ?)",
                productos_ejemplo
            )
            self.conn.commit()

    def default_receipt_template(self):
        """Plantilla HTML por defecto para recibos."""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; font-size: 10pt; }
        .recibo { width: 300px; margin: 0 auto; border: 1px dashed #333; padding: 15px; }
        h1 { font-size: 16pt; text-align: center; margin: 0 0 10px 0; }
        .info { text-align: center; margin-bottom: 15px; font-size: 9pt; }
        .detail { margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 10px; }
        .item { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 9pt; }
        .total-section { margin-top: 15px; border-top: 2px solid #333; padding-top: 10px; }
        .total { font-weight: bold; font-size: 12pt; }
        .footer { margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 10px; text-align: center; font-size: 8pt; }
    </style>
</head>
<body>
    <div class="recibo">
        <h1>{{NOMBRE_NEGOCIO}}</h1>
        <div class="info">
            <p><strong>Venta ID:</strong> {{ID_VENTA}}</p>
            <p><strong>Fecha:</strong> {{FECHA}}</p>
        </div>
        
        <div class="detail">
            <div style="font-weight: bold; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-bottom: 5px;" class="item">
                <span>Producto</span><span>Cant. / Subtotal</span>
            </div>
            <!-- ITEMS_PLACEHOLDER -->
        </div>

        <div class="total-section">
            <div class="item total"><span>TOTAL A PAGAR:</span><span>${{TOTAL}}</span></div>
            <div class="item"><span>MONTO RECIBIDO:</span><span>${{MONTO_PAGADO}}</span></div>
            <div class="item"><span>VUELTO:</span><span>${{VUELTO}}</span></div>
        </div>

        <div class="footer">
            <p>¡Gracias por su compra!</p>
            <p>Vuelva pronto</p>
        </div>
    </div>
</body>
</html>"""

    def get_config(self, clave, default=None):
        """Obtiene un valor de configuración."""
        result = self.fetch("SELECT valor FROM Configuracion WHERE clave = ?", (clave,))
        return result[0][0] if result else default

    def set_config(self, clave, valor):
        """Establece o actualiza un valor de configuración."""
        self.execute(
            "INSERT OR REPLACE INTO Configuracion (clave, valor) VALUES (?, ?)",
            (clave, valor)
        )

    def fetch(self, query, params=()):
        """Ejecuta una consulta SELECT y retorna los resultados."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error de DB", f"Error en consulta: {e}")
            return []

    def execute(self, query, params=()):
        """Ejecuta una consulta INSERT/UPDATE/DELETE."""
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            messagebox.showerror("Error de DB", f"Error en operación: {e}")
            return None

    def close(self):
        """Cierra la conexión a la base de datos."""
        self.conn.close()