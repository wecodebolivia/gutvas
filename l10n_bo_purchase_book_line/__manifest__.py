{
    'name': 'Libro de Compras Bolivia',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Libro de Compras para Bolivia',
    'description': 'Generación del libro de compras según normativa boliviana.',
    'author': 'Tu Nombre o Empresa',
    'depends': [
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        # 'wizard/libro_compras_wizard_view.xml',  # Comentado porque aún no existe
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
