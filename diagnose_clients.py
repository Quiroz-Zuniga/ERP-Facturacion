#!/usr/bin/env python3
"""
Script de diagnóstico para el módulo de clientes
"""

import sys
import traceback
import tkinter as tk
from tkinter import ttk

print("🔍 DIAGNÓSTICO DEL MÓDULO DE CLIENTES")
print("="*50)

try:
    print("1. Importando base de datos...")
    from database import DBManager
    db = DBManager()
    print("   ✅ DBManager importado correctamente")
    
    print("2. Verificando tabla Clientes...")
    clientes = db.fetch("SELECT * FROM Clientes LIMIT 5")
    print(f"   ✅ Encontrados {len(clientes)} clientes en la BD")
    for cliente in clientes:
        print(f"      - ID {cliente[0]}: {cliente[1]} {cliente[2]}")
    
    print("3. Importando módulo de clientes...")
    from frames.clients import ClientsFrame
    print("   ✅ ClientsFrame importado correctamente")
    
    print("4. Creando ventana de prueba...")
    root = tk.Tk()
    root.title("Test ClientsFrame")
    root.geometry("1200x800")
    
    print("5. Simulando estructura de la app...")
    class MockApp:
        def __init__(self):
            self.db = db
    
    app = MockApp()
    
    print("6. Creando frame de clientes...")
    try:
        frame = ClientsFrame(root, app)
        print("   ✅ ClientsFrame creado sin errores")
        
        print("7. Empaquetando frame...")
        frame.pack(fill='both', expand=True)
        print("   ✅ Frame empaquetado correctamente")
        
        print("8. Verificando componentes internos...")
        if hasattr(frame, 'tree'):
            items = frame.tree.get_children()
            print(f"   ✅ Tree view tiene {len(items)} elementos")
        else:
            print("   ❌ Tree view no encontrado")
            
        if hasattr(frame, 'nombre_entry'):
            print("   ✅ Formulario de entrada encontrado")
        else:
            print("   ❌ Formulario de entrada no encontrado")
            
        print("9. Cerrando ventana de prueba...")
        root.destroy()
        print("   ✅ Prueba completada exitosamente")
        
    except Exception as e:
        print(f"   ❌ Error al crear ClientsFrame: {e}")
        traceback.print_exc()
        root.destroy()

except Exception as e:
    print(f"❌ Error general: {e}")
    traceback.print_exc()

print("\n🎯 DIAGNÓSTICO COMPLETADO")