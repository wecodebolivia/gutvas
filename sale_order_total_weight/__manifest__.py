# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Total Weight',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Muestra el peso total de los productos en cotizaciones y pedidos de venta',
    'description': '''
        Sale Order Total Weight
        =======================
        Este modulo agrega un campo calculado que muestra el peso total 
        de todos los productos en una cotizacion u orden de venta.
        
        El peso se obtiene del campo 'weight' (Peso) configurado en la 
        pestana Inventario de cada producto.
        
        Caracteristicas:
        ----------------
        * Calculo automatico del peso total basado en cantidad * peso del producto
        * Visible en la vista de formulario de cotizaciones/pedidos
        * Actualizacion en tiempo real al agregar/modificar lineas
        * Reporte PDF con peso total incluido
    ''',
    'author': 'Juan Luis Garvia - Largotek SRL',
    'website': 'https://www.largotek.com',
    'maintainer': 'Juan Luis Garvia',
    'support': 'info@largotek.com',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'stock',
    ],
    'data': [
        'views/sale_order_view.xml',
        'reports/sale_order_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
