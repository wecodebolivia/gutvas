# -*- coding: utf-8 -*-
{
    'name': 'Warehouse Auto Routes',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Automatic inter-warehouse transport route creation',
    'description': """
        Warehouse Auto Routes
        =====================
        
        Este módulo automatiza la creación de rutas de transporte entre almacenes.
        
        Características:
        ----------------
        * Creación automática de rutas entre todos los almacenes al instalar/actualizar el módulo
        * Sistema de safeguard que evita duplicación de rutas
        * Rutas bidireccionales: Almacén A → B y B → A
        * Operaciones de envío y recepción configuradas automáticamente
        * Wizard para generar rutas manualmente si es necesario
        * Detección inteligente de rutas existentes por external_id
        
        Flujo de trabajo:
        -----------------
        1. Salida del Almacén 1 (Delivery Order)
        2. Tránsito en ruta hacia Almacén 2 (Internal Transfer)
        3. Recepción en Almacén 2 (Receipt)
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
