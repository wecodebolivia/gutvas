# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo.http import request
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
from odoo.osv import expression  # ✅ Importación corregida
import odoo.addons.decimal_precision as dp
import operator


class MainHide(models.Model):
    _name = "multi.main.hide"
    _description = "Menu Visibility Restriction"

    company_id = fields.Many2one('res.company', string="Company")
    ui_menu_id = fields.Many2one('ir.ui.menu', string="Menu")
    user_id = fields.Many2many("res.users", string="Users", required=True)


class ResCompany(models.Model):
    _inherit = "res.company"

    main_hide_ids = fields.One2many("multi.main.hide", 'company_id', string="Hide Menus")


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @api.returns('self')
    def get_menus_users(self):
        dropdown_company_id = request.httprequest.cookies.get('cids') or ''
        current_company = self.env.user.company_id
        if dropdown_company_id:
            current_company = self.env['res.company'].browse(int(dropdown_company_id))
        user_company = self.env['res.company'].browse(current_company.id)

        if self.env.user.has_group('show_hide_menu_multi_company_app.group_hide_menu'):
            return user_company.main_hide_ids
        return False

    @api.model
    def load_menus(self, debug):
        main_list = []
        lat_list = []
        menu_sub_roots = []
        fields_to_read = ['name', 'sequence', 'parent_id', 'action', 'web_icon', 'web_icon_data']

        menu_roots = self.get_user_roots()
        for menu in menu_roots:
            main_list.append(menu.id)

        current_user = self.env.user
        menu_ro = self.get_menus_users()

        if menu_ro:
            for record in menu_ro:
                if current_user in record.user_id:
                    lat_list.append(record.ui_menu_id.id)
            menu_sub_roots = list(set(main_list) - set(lat_list))
            menu_roots = self.search([('id', 'in', menu_sub_roots), ('parent_id', '=', False)])

        menu_roots_data = menu_roots.read(fields_to_read) if menu_roots else []
        menu_root = {
            'id': False,
            'name': 'root',
            'parent_id': [-1, ''],
            'children': [menu['id'] for menu in menu_roots_data],
        }

        all_menus = {'root': menu_root}

        if not menu_roots_data:
            return all_menus

        menus_domain = [('id', 'child_of', menu_roots.ids)]
        blacklisted_menu_ids = self._load_menus_blacklist()
        if blacklisted_menu_ids:
            menus_domain = expression.AND([menus_domain, [('id', 'not in', blacklisted_menu_ids)]])
        menus = self.search(menus_domain)
        menu_items = menus.read(fields_to_read)
        xmlids = (menu_roots + menus)._get_menuitems_xmlids()

        allowed_ids = set(menus.ids) - set(lat_list)
        menus = self.search([('id', 'in', list(allowed_ids))])
        menu_items = menus.read(fields_to_read)
        menu_items.extend(menu_roots_data)

        menu_items_map = {menu["id"]: menu for menu in menu_items}
        for menu_item in menu_items:
            menu_item.setdefault('children', [])
            parent_id = menu_item['parent_id'] and menu_item['parent_id'][0]
            menu_item['xmlid'] = xmlids.get(menu_item['id'], "")
            if parent_id in menu_items_map:
                menu_items_map[parent_id].setdefault('children', []).append(menu_item['id'])

        all_menus.update(menu_items_map)

        for menu_id in all_menus:
            all_menus[menu_id]['children'].sort(key=lambda id: all_menus[id]['sequence'])

        def _set_app_id(app_id, menu):
            menu['app_id'] = app_id
            for child_id in menu['children']:
                _set_app_id(app_id, all_menus[child_id])

        for app in menu_roots_data:
            app_id = app['id']
            _set_app_id(app_id, all_menus[app_id])

        all_menus = {menu['id']: menu for menu in all_menus.values() if menu.get('app_id')}
        all_menus['root'] = menu_root

        return all_menus
