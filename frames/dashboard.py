# frames/dashboard.py
"""
Dashboard profesional moderno con múltiples KPIs, gráficas con scroll y alertas animadas.
Estilo Microsoft Dynamics.
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class DashboardFrame(ttk.Frame):
    """Dashboard profesional con KPIs, alertas y gráficas modernas."""

    def __init__(self, parent, app):
        super().__init__(parent, padding=10)
        self.app = app
        self.db = app.db

# ------------------ Canvas principal ------------------
        self.canvas = tk.Canvas(self, bg="#f0f2f5")
        self.v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        self.scrollable_frame = ttk.Frame(self.canvas)

# Vincular tamaño del frame al canvas
        self.scrollable_frame.bind(
           "<Configure>",
           lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

# Empaquetar todo
        self.canvas.pack(side="top", fill="both", expand=True)
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")

        # Empaquetar
        self.canvas.pack(side="top", fill="both", expand=True)
        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")

# -------------------- Scroll con rueda del mouse --------------------
        def _on_mousewheel(event):
          # Scroll vertical
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _on_shift_mousewheel(event):
            # Scroll horizontal si se mantiene Shift
            self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")

# Vincular eventos
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)         # Windows / Mac
        self.canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)  # Shift + rueda para horizontal

        # ------------------ Datos ------------------
        self.load_data()
        self.render_dashboard()

    # -------------------- Cargar datos --------------------
    def load_data(self):
        """Carga los datos desde la base de datos."""
        self.total_sales = self.db.fetch("SELECT SUM(total) FROM Ventas")[0][0] or 0
        self.daily_sales = self.db.fetch("SELECT SUM(total) FROM Ventas WHERE DATE(fecha)=DATE('now')")[0][0] or 0
        self.monthly_sales = self.db.fetch("SELECT SUM(total) FROM Ventas WHERE strftime('%m', fecha)=strftime('%m','now')")[0][0] or 0

        self.low_stock = self.db.fetch(
            "SELECT nombre, stock FROM Productos WHERE stock <= 10 ORDER BY stock ASC"
        )

        best_seller_data = self.db.fetch("""
            SELECT nombre_producto, SUM(cantidad)
            FROM DetalleVenta
            GROUP BY nombre_producto
            ORDER BY SUM(cantidad) DESC
            LIMIT 1
        """)
        self.best_seller = best_seller_data[0] if best_seller_data else ("N/A", 0)

        self.total_products = self.db.fetch("SELECT COUNT(*) FROM Productos")[0][0] or 0

        # Ventas por mes y por día
        ventas_mes = self.db.fetch("""
            SELECT strftime('%m', fecha), SUM(total)
            FROM Ventas
            GROUP BY strftime('%m', fecha)
            ORDER BY strftime('%m', fecha)
        """)
        self.ventas_por_mes = ventas_mes or []

        ventas_dia = self.db.fetch("""
            SELECT strftime('%d', fecha), SUM(total)
            FROM Ventas
            WHERE strftime('%m', fecha)=strftime('%m','now')
            GROUP BY strftime('%d', fecha)
        """)
        self.ventas_por_dia = ventas_dia or []

    # -------------------- Render del Dashboard --------------------
    def render_dashboard(self):
        # -------------------- Título --------------------
        ttk.Label(
            self.scrollable_frame, text="📊 Dashboard Moderno",
            font=("Segoe UI", 18, "bold"), foreground="#333"
        ).grid(row=0, column=0, columnspan=3, pady=(0,20), sticky="w")

        # -------------------- KPIs --------------------
        kpi_width = 220
        kpi_height = 110

        def kpi_card(row, col, title, value, color, description):
            card = tk.Frame(self.scrollable_frame, width=kpi_width, height=kpi_height, bg="#ffffff", relief="raised", bd=2)
            card.grid(row=row, column=col, padx=10, pady=10)
            card.grid_propagate(False)
            card.columnconfigure(0, weight=1)

            tk.Label(card, text=title, font=("Segoe UI", 10), bg="#ffffff", fg="#6c757d").pack(anchor="w", padx=10, pady=(10,5))
            val_label = tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), bg="#ffffff", fg=color)
            val_label.pack(anchor="w", padx=10, pady=2)
            self.animate_counter(val_label, value)

            ttk.Separator(card, orient="horizontal").pack(fill="x", padx=10, pady=5)
            tk.Label(card, text=description, font=("Segoe UI", 8), bg="#ffffff", fg="#adb5bd").pack(anchor="w", padx=10, pady=(0,10))


        # Fila 1
        kpi_card(1, 0, "Ventas Totales", f"${self.total_sales:,.2f}", "#007bff", "Total acumulado")
        kpi_card(1, 1, "Ventas Mensuales", f"${self.monthly_sales:,.2f}", "#28a745", "Total del mes")
        kpi_card(1, 2, "Ventas Diarias", f"${self.daily_sales:,.2f}", "#ffc107", "Hoy")
        # Fila 2
        kpi_card(2, 0, "Stock Bajo", f"{len(self.low_stock)} items", "#dc3545", "Productos < 10 unidades")
        kpi_card(2, 1, "Producto Más Vendido", f"{self.best_seller[0][:20]}...", "#17a2b8", f"{self.best_seller[1]} vendidos")
        kpi_card(2, 2, "Total Productos", f"{self.total_products}", "#6f42c1", "Inventario total")

        # -------------------- Gráficas --------------------
        self.create_bar_chart(self.ventas_por_mes, "📈 Ventas Mensuales", "Mes", "Monto ($)", row=3, column=0, columnspan=2)
        self.create_line_chart(self.ventas_por_dia, "📊 Ventas Diarias", "Día", "Monto ($)", row=3, column=2, columnspan=1)
        self.create_pie_chart(self.low_stock, "🚨 Stock Bajo", "# Productos", row=4, column=0, columnspan=1)

        # -------------------- Botón actualizar --------------------
        ttk.Button(self.scrollable_frame, text="🔄 Actualizar Dashboard", command=self.refresh_dashboard).grid(row=5, column=0, columnspan=3, pady=20)

    # -------------------- Animación KPIs --------------------
    def animate_counter(self, label, target_value):
        def run():
            try:
                if isinstance(target_value, str) and target_value.startswith("$"):
                    num = float(target_value.replace("$","").replace(",",""))
                    step = max(1,int(num/50))
                    for i in range(0,int(num)+1,step):
                        label.config(text=f"${i:,.0f}")
                        time.sleep(0.02)
                    label.config(text=f"${num:,.2f}")
                elif isinstance(target_value, str) and "items" in target_value:
                    num = int(target_value.replace(" items",""))
                    for i in range(num+1):
                        label.config(text=f"{i} items")
                        time.sleep(0.02)
                else:
                    label.config(text=target_value)
            except:
                label.config(text=target_value)
        threading.Thread(target=run, daemon=True).start()

    # -------------------- Gráficas --------------------
    def create_bar_chart(self, data, title, xlabel, ylabel, row=0, column=0, columnspan=1):
        chart_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding=5)
        chart_frame.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=5, pady=5)

        if not data:
            ttk.Label(chart_frame, text="No hay datos", font=("Segoe UI",10)).pack()
            return

        # Ajustamos el tamaño de la figura al frame (más ancho si hay muchos datos)
        fig_width = max(6, len(data) * 0.5)  # Ajusta según cantidad de datos
        fig = Figure(figsize=(fig_width,3), dpi=70)
        ax = fig.add_subplot(111)
        x = [d[0] for d in data]
        y = [d[1] for d in data]
        ax.bar(x, y, color="#007bff", alpha=0.6)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(axis='y', linestyle='--', alpha=0.6)

        canvas_fig = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas_fig.get_tk_widget().pack(fill="both", expand=True)
        canvas_fig.draw()


    def create_line_chart(self, data, title, xlabel, ylabel, row=0, column=0, columnspan=1):
        chart_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding=5)
        chart_frame.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=5, pady=5)

        if not data:
            ttk.Label(chart_frame, text="No hay datos", font=("Segoe UI",10)).pack()
            return

        fig_width = max(5, len(data) * 0.5)
        fig = Figure(figsize=(fig_width,3), dpi=70)
        ax = fig.add_subplot(111)
        x = [d[0] for d in data]
        y = [d[1] for d in data]
        ax.plot(x, y, marker="o", color="#28a745")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(axis='y', linestyle='--', alpha=0.6)

        canvas_fig = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas_fig.get_tk_widget().pack(fill="both", expand=True)
        canvas_fig.draw()

    def create_pie_chart(self, data, title, label_field, row=0, column=0, columnspan=1):
        chart_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding=5)
        chart_frame.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=5, pady=5)

        canvas = tk.Canvas(chart_frame)
        v_scroll = ttk.Scrollbar(chart_frame, orient="vertical", command=canvas.yview)
        inner_frame = ttk.Frame(canvas)
        inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        if not data:
            ttk.Label(inner_frame, text="No hay datos", font=("Segoe UI",10)).pack()
            return

        fig = Figure(figsize=(4,3), dpi=80)
        ax = fig.add_subplot(111)
        labels = [d[0] for d in data]
        sizes = [d[1] for d in data]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=["#007bff","#28a745","#ffc107","#dc3545","#6f42c1"])
        ax.axis('equal')

        canvas_fig = FigureCanvasTkAgg(fig, master=inner_frame)
        canvas_fig.get_tk_widget().pack(fill="both", expand=True)
        canvas_fig.draw()

    # -------------------- Refresh --------------------
    def refresh_dashboard(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.load_data()
        self.render_dashboard()
# -------------------- Gráficas ajustadas --------------------
def create_bar_chart(self, data, title, xlabel, ylabel, row=0, column=0, columnspan=1):
    chart_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding=10)
    chart_frame.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=5, pady=5)

    if not data:
        ttk.Label(chart_frame, text="No hay datos", font=("Segoe UI", 10)).pack()
        return

    fig = Figure(figsize=(6, 4), dpi=80)
    ax = fig.add_subplot(111)
    x = [d[0] for d in data]
    y = [d[1] for d in data]
    ax.bar(x, y, color="#007bff", alpha=0.7)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Rotar etiquetas si hay muchas
    if len(x) > 5:
        ax.set_xticklabels(x, rotation=45, ha="right")

    fig.tight_layout()  # Ajusta todo dentro de la figura

    canvas_fig = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas_fig.get_tk_widget().pack(fill="both", expand=True)
    canvas_fig.draw()


def create_line_chart(self, data, title, xlabel, ylabel, row=0, column=0, columnspan=1):
    chart_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding=10)
    chart_frame.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=5, pady=5)

    if not data:
        ttk.Label(chart_frame, text="No hay datos", font=("Segoe UI", 10)).pack()
        return

    fig = Figure(figsize=(6, 4), dpi=80)
    ax = fig.add_subplot(111)
    x = [d[0] for d in data]
    y = [d[1] for d in data]
    ax.plot(x, y, marker="o", color="#28a745")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    if len(x) > 5:
        ax.set_xticklabels(x, rotation=45, ha="right")

    fig.tight_layout()

    canvas_fig = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas_fig.get_tk_widget().pack(fill="both", expand=True)
    canvas_fig.draw()


def create_pie_chart(self, data, title, label_field, row=0, column=0, columnspan=1):
    chart_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding=10)
    chart_frame.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=5, pady=5)

    if not data:
        ttk.Label(chart_frame, text="No hay datos", font=("Segoe UI", 10)).pack()
        return

    fig = Figure(figsize=(4, 4), dpi=80)
    ax = fig.add_subplot(111)
    labels = [d[0] for d in data]
    sizes = [d[1] for d in data]
    colors = ["#007bff","#28a745","#ffc107","#dc3545","#6f42c1"]
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(labels)])
    ax.axis('equal') 

    fig.tight_layout()

    canvas_fig = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas_fig.get_tk_widget().pack(fill="both", expand=True)
    canvas_fig.draw()


    # -------------------- Refresh --------------------
    def refresh_dashboard(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.load_data()
        self.render_dashboard()
