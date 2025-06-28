from odoo import models, fields

class EjemploModelo(models.Model):
    _name = 'ejemplo.modelo'
    _description = 'Ejemplo Modelo'

    name = fields.Char(string='Nombre')
