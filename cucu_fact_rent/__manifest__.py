# -*- coding: utf-8 -*-
{
    'name': 'CUCU - Facturación Electrónica Sector Alquileres',
    'version': '1.0.0',
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
        * Anulación y reversión de facturas de alquileres
        * Gestión automática de tokens JWT con renovación
        * CAFC configurables (sandbox/producción)
        * Logging detallado para debugging
        
        Endpoints:
        ==========
        * POST /auth/login (autenticación independiente)
        * POST /api/v1/invoice/electronic/rent
        * POST /api/v1/invoice/electronic/rent/anulation
        * POST /api/v1/invoice/electronic/rent/revert
        
        IMPORTANTE:
        ===========
        Este módulo es INDEPENDIENTE de cucu_fact_core.
        Usa su propio sistema de autenticación y credenciales.
        
        Autor: LargoTek / WeCodeBolivia
        Versión: 1.0.0
    ''',
    'author': 'LargoTek',
    'website': 'https://www.largotek.com',
    'depends': [
        'account',
        'l10n_bo',
        'cucu_fact_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/account_move_views.xml',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
