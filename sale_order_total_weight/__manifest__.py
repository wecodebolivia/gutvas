# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Total Weight',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Muestra el peso total de los productos en cotizaciones y pedidos de venta',
    'description': '''
        Sale Order Total Weight
        =======================
        Este módulo agrega un campo calculado que muestra el peso total 
        de todos los productos en una cotización u orden de venta.
        
        El peso se obtiene del campo 'weight' (Peso) configurado en la 
        pestaña Inventario de cada producto.
        
        Características:
        ----------------
        * Cálculo automático del peso total basado en cantidad * peso del producto
        * Visible en la vista de formulario de cotizaciones/pedidos
        * Actualización en tiempo real al agregar/modificar líneas
    ''',
    'author': 'Juan Luis Garvía - Largotek SRL',
    'website': 'https://www.largotek.com',
    'maintainer': 'Juan Luis Garvía',
    'support': 'info@largotek.com',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'stock',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
