{
    'name': 'Comprobantes contables BO',
    'version': '18.0.1.0',
    'category': 'Accounting',
    'license': 'OPL-1',
    'summary': 'PERMITE LA IMPRESIÓN DE COMPROBANTES CONTABLES',
    'description': """...""",
    'author': 'Largotek SRL',
    'website': 'https://www.largotek.com',
    'depends': ['account'],
    'data': [
        'report/payment_receipt_report.xml',
        'report/report_journal_entries.xml',
        'report/report_journal_entries_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    # Elimina completamente la sección 'assets' si no tienes archivos CSS/SCSS
    "images": ["static/description/Banner.gif"],
}