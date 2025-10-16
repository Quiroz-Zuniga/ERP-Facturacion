#!/usr/bin/env python3
"""
Script de prueba para verificar que las ventas con clientes funcionan
"""

import sqlite3
from datetime import datetime

print("🧪 PRUEBA DE VENTAS CON CLIENTES")
print("="*50)

# Conectar a la base de datos
conn = sqlite3.connect('erp_profesional.db')
cursor = conn.cursor()

try:
    # 1. Verificar estructura de la tabla Ventas
    print("1. Verificando estructura de tabla Ventas...")
    cursor.execute("PRAGMA table_info(Ventas);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"   Columnas: {', '.join(column_names)}")
    
    if 'id_cliente' in column_names:
        print("   ✅ Columna id_cliente encontrada")
    else:
        print("   ❌ Columna id_cliente NO encontrada")
        
    # 2. Verificar clientes disponibles
    print("\n2. Verificando clientes disponibles...")
    cursor.execute("SELECT id, nombre, apellido FROM Clientes WHERE activo = 1 LIMIT 3;")
    clientes = cursor.fetchall()
    print(f"   Clientes activos: {len(clientes)}")
    for cliente in clientes:
        print(f"      - ID {cliente[0]}: {cliente[1]} {cliente[2]}")
    
    # 3. Simular una venta con cliente
    print("\n3. Simulando venta con cliente...")
    if clientes:
        cliente_id = clientes[0][0]  # Usar el primer cliente
        venta_id = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insertar venta de prueba
        cursor.execute("""
            INSERT INTO Ventas (id, fecha, total, monto_pagado, vuelto, usuario_id, id_cliente, tipo_recibo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (venta_id, fecha, 100.0, 100.0, 0.0, 1, cliente_id, "TEST"))
        
        print(f"   ✅ Venta {venta_id} creada para cliente ID {cliente_id}")
        
        # Verificar que se guardó correctamente
        cursor.execute("SELECT * FROM Ventas WHERE id = ?", (venta_id,))
        venta = cursor.fetchone()
        if venta:
            print(f"   ✅ Venta verificada - Cliente ID: {venta[6]}")
        else:
            print("   ❌ Error: Venta no encontrada")
        
        # Limpiar venta de prueba
        cursor.execute("DELETE FROM Ventas WHERE id = ?", (venta_id,))
        print("   🧹 Venta de prueba eliminada")
    else:
        print("   ❌ No hay clientes disponibles para prueba")
    
    # 4. Verificar relación con ventas existentes
    print("\n4. Verificando ventas existentes con clientes...")
    cursor.execute("SELECT COUNT(*) FROM Ventas WHERE id_cliente IS NOT NULL;")
    ventas_con_cliente = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Ventas WHERE id_cliente IS NULL;")
    ventas_sin_cliente = cursor.fetchone()[0]
    
    print(f"   Ventas con cliente: {ventas_con_cliente}")
    print(f"   Ventas sin cliente: {ventas_sin_cliente}")
    
    conn.commit()
    print("\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")

except Exception as e:
    print(f"\n❌ ERROR EN PRUEBAS: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    conn.close()
    print("\n🔒 Conexión a base de datos cerrada")