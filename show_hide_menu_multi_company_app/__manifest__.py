# -*- coding: utf-8 -*-

{
    'name': 'Hide Menu on Multi Company for Users',
    "author": "Edge Technologies",
    'version': '15.0.1.0',
    'live_test_url': "https://youtu.be/21FIpMU24TU",
    "images":['static/description/main_screenshot.png'],
    'summary': "Company show hide menu feature user hide menu from user limited menu access to user multi company menu restriction to user multi company show hide feature multi company show hide menu feature multi company user hide menu multi company hide menu from user",
    'description': """This app will allow to hide main menus and also sub menus.
        Menu or sub menu will invisible for particular company and for particular users.

   
   Menu hide/show for user in odoo hide menu for user in odoo show menu for user. visible and invisible menu for user in odoo.
   User generic security restriction for menu in odoo. odoo hide menu by security groups in odoo hide menu from a specific user.
    Restrict menu from a specific user. hide any menu for user in odoo restrict user menus in odoo from settings. odoo user menu restriction.
    Hide any menu and submenu for specific user. security for menu and submenu. display or hide particular menu for specific user

Show hide feature
Show hide menu feature
User hide menu 
Hide menu from user 
Limied menu access to user
Restricted menu access to user
Menu wise restricion
Show menu to user

Multi company menu restriction to user
Multi company show hide feature
Multi company show hide menu feature
Multi company user hide menu 
Multi companyhide menu from user 
Multi company limited menu access to user
Multi company restricted menu access to user
Multi company menu wise restricion
Multi company show menu to user
Multi company menu restriction to user
Generic security restriction 
Mutli-company security restriction
Multiple company generic security restriction

 
    """,
    "license" : "OPL-1",
    'depends': ['base','sale_management','purchase','stock'],
    'data': [
            'security/hide_menu_security.xml',
            'security/ir.model.access.csv',
            'views/view_main_hide.xml',
            ],
    'installable': True,
    'auto_install': False,
    'price': 10,
    'currency': "EUR",
    'category': 'Extra Tools',
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
