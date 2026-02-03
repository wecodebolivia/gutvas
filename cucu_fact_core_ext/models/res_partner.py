# -*- coding: utf-8 -*-
###################################################################################
# Copyright (c) 2021-Present cucu | soluciones digitales (https://cucu.bo)
###################################################################################

from odoo import models, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains('nit_client')
    def _check_nit_client_numeric(self):
        """Validate that nit_client field contains only numeric characters."""
        for record in self:
            if record.nit_client and not record.nit_client.isdigit():
                raise ValidationError(
                    "El campo 'Number Document' solo puede contener números."
                )
