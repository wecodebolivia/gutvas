# -*- coding: utf-8 -*-
{
    'name': 'CUCU - Facturación Electrónica Sector Alquileres',
    'version': '1.0.4',
    'category': 'Accounting/Localizations',
    'summary': 'Integración CUCU API para sector alquileres Bolivia',
    'description': '''
        Módulo de facturación electrónica para el sector alquileres
        según normativa del Servicio de Impuestos Nacionales (SIN) Bolivia.

        Características:
        =================
        * Integración con endpoints específicos CUCU para alquileres
        * Credenciales y tokens INDEPENDIENTES (no usa cucu_fact_core)
        * Campos obligatorios: período facturado (billedPeriod)
        * Ciudad (clientCity) desde sucursal CUCU configurada en compañía
        * Anulación y reversión de facturas de alquileres (con wizard)
        * Recuperación de datos post-emisión (invoiceCode + invoiceNumber)
        * Gestión automática de tokens JWT con renovación
        * CAFC configurables (sandbox/producción)
        * Logging detallado para debugging
        * Reporte A4 específico: título "FACTURA DE ALQUILER" + Período Facturado

        Endpoints:
        ==========
        * POST /auth/login
        * POST /api/v1/invoice/electronic/rent
        * GET  /api/v1/invoice/electronic/rent/status
        * POST /api/v1/invoice/electronic/rent/anulation
        * POST /api/v1/invoice/electronic/rent/revert

        Autor: LargoTek / WeCodeBolivia
        Versión: 1.0.4
    ''',
    'author': 'LargoTek',
    'website': 'https://www.largotek.com',
    'depends': [
        'account',
        'l10n_bo',
        'cucu_fact_core',
        'cucu_fact_report_ext',  # Necesario para MRO correcto en render_invoice()
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'views/report_template_a4_rent.xml',
        'wizards/cucu_rent_anulation_wizard.xml',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
