"""
frames/dashboard.py
Panel principal con métricas y alertas del negocio
"""
from tkinter import ttk
import tkinter as tk


class DashboardFrame(ttk.Frame):
    """Panel de control principal con KPIs y alertas."""
    
    def __init__(self, parent, app):
        super().__init__(parent, padding="20")
        self.app = app
        self.db = app.db
        
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.load_data()
        self.render_dashboard()

    def load_data(self):
        """Carga los datos estadísticos desde la base de datos."""
        # Total de ventas
        total_sales_data = self.db.fetch("SELECT SUM(total) FROM Ventas")
        self.total_sales = total_sales_data[0][0] or 0.0
        
        # Productos con stock bajo (menos de 10)
        low_stock_data = self.db.fetch(
            "SELECT nombre, stock FROM Productos WHERE stock <= 10 ORDER BY stock ASC"
        )
        self.low_stock = low_stock_data
        
        # Producto más vendido
        best_seller_data = self.db.fetch("""
            SELECT nombre_producto, SUM(cantidad) AS total_vendido
            FROM DetalleVenta
            GROUP BY nombre_producto
            ORDER BY total_vendido DESC
            LIMIT 1
        """)
        self.best_seller = best_seller_data[0] if best_seller_data else ("N/A", 0)
        
        # Total de productos
        total_products = self.db.fetch("SELECT COUNT(*) FROM Productos")
        self.total_products = total_products[0][0] if total_products else 0

    def render_dashboard(self):
        """Renderiza los componentes del dashboard."""
        # Título
        ttk.Label(
            self, 
            text="Panel de Control", 
            font=('Arial', 20, 'bold')
        ).grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        # KPI Cards
        self.create_kpi_card(
            1, 0, 
            "Ventas Totales", 
            f"${self.total_sales:,.2f}", 
            "#007bff",
            "Total acumulado de todas las ventas"
        )
        
        self.create_kpi_card(
            1, 1, 
            "Productos en Stock Bajo", 
            f"{len(self.low_stock)} items", 
            "#dc3545",
            "Productos con menos de 10 unidades"
        )
        
        self.create_kpi_card(
            1, 2, 
            "Producto Más Vendido", 
            f"{self.best_seller[0][:20]}...", 
            "#28a745",
            f"{self.best_seller[1]} unidades vendidas"
        )
        
        # Tabla de alertas de stock bajo
        self.create_low_stock_alert()

    def create_kpi_card(self, row, col, title, value, color, description):
        """Crea una tarjeta KPI con diseño profesional."""
        card = ttk.Frame(self, relief="raised", borderwidth=2)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Título
        ttk.Label(
            card, 
            text=title, 
            font=('Arial', 11), 
            foreground="#6c757d"
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        # Valor principal
        value_label = ttk.Label(
            card, 
            text=value, 
            font=('Arial', 24, 'bold'), 
            foreground=color
        )
        value_label.pack(anchor="w", padx=15, pady=5)
        
        # Separador
        ttk.Separator(card, orient='horizontal').pack(fill="x", padx=15, pady=10)
        
        # Descripción
        ttk.Label(
            card, 
            text=description, 
            font=('Arial', 9), 
            foreground="#adb5bd"
        ).pack(anchor="w", padx=15, pady=(0, 15))

    def create_low_stock_alert(self):
        """Crea la sección de alertas de stock bajo."""
        alert_frame = ttk.LabelFrame(
            self, 
            text="🚨 Alertas de Inventario", 
            padding="15"
        )
        alert_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=20)
        
        if not self.low_stock:
            ttk.Label(
                alert_frame, 
                text="✅ No hay productos con stock bajo. ¡Todo en orden!", 
                font=('Arial', 12),
                foreground="#28a745"
            ).pack(pady=20)
            return
        
        # Crear Treeview para mostrar productos con stock bajo
        tree = ttk.Treeview(
            alert_frame, 
            columns=("Producto", "Stock", "Estado"), 
            show="headings", 
            height=8
        )
        
        tree.heading("Producto", text="Producto")
        tree.heading("Stock", text="Stock Disponible")
        tree.heading("Estado", text="Estado")
        
        tree.column("Producto", width=400)
        tree.column("Stock", width=150, anchor="center")
        tree.column("Estado", width=150, anchor="center")
        
        tree.pack(fill="both", expand=True)
        
        # Llenar con datos
        for nombre, stock in self.low_stock:
            if stock <= 5:
                estado = "🔴 CRÍTICO"
                tag = 'critical'
            elif stock <= 10:
                estado = "🟡 BAJO"
                tag = 'warning'
            else:
                estado = "🟢 OK"
                tag = 'ok'
            
            tree.insert("", "end", values=(nombre, stock, estado), tags=(tag,))
        
        # Configurar colores de tags
        tree.tag_configure('critical', background='#f8d7da', foreground='#721c24')
        tree.tag_configure('warning', background='#fff3cd', foreground='#856404')
        tree.tag_configure('ok', background='#d4edda', foreground='#155724')
        
        # Botón para refrescar
        ttk.Button(
            alert_frame, 
            text="🔄 Actualizar Dashboard", 
            command=self.refresh_dashboard
        ).pack(pady=10)

    def refresh_dashboard(self):
        """Recarga los datos del dashboard."""
        for widget in self.winfo_children():
            widget.destroy()
        
        self.load_data()
        self.render_dashboard()