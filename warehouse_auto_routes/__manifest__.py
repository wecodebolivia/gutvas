# -*- coding: utf-8 -*-
{
    'name': 'Warehouse Auto Routes',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Automatic inter-warehouse transport route creation with internal transfers',
    'description': """
        Warehouse Auto Routes
        =====================
        
        Este módulo automatiza la creación de rutas de transporte entre almacenes 
        usando transferencias internas y ubicaciones en tránsito.
        
        Características:
        ----------------
        * Creación automática de rutas entre todos los almacenes al instalar/actualizar el módulo
        * Sistema de safeguard que evita duplicación de rutas y ubicaciones
        * Rutas bidireccionales: Almacén A → B y B → A
        * Ubicaciones en tránsito automáticas para cada ruta
        * Operaciones de transferencia interna configuradas automáticamente
        * Wizard para generar rutas manualmente si es necesario
        * Detección inteligente de rutas existentes por external_id
        
        Flujo de trabajo (2 pasos):
        ---------------------------
        1. Transferencia Interna: Stock Almacén A → Ubicación en Tránsito (A→B)
           - Responsable en Almacén A valida el envío
           
        2. Transferencia Interna: Ubicación en Tránsito (A→B) → Stock Almacén B
           - Responsable en Almacén B recibe y valida el ingreso
           
        Ventajas:
        ---------
        * Solo transferencias internas (no mezcla con recepciones/entregas)
        * Visibilidad total de productos en tránsito
        * Control bidireccional (origen y destino validan)
        * Trazabilidad completa de movimientos
        * Ubicación dedicada para cada ruta
    """,
    'author': 'WeCode Bolivia',
    'website': 'https://www.wecodebolivia.com',
    'license': 'LGPL-3',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/warehouse_route_generator_views.xml',
        'views/stock_warehouse_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
