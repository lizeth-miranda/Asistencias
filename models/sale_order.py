# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class Cuenta(models.Model):
    _inherit = 'sale.order'

    analytic_account_id = fields.Many2one(
        required=False,
    )
