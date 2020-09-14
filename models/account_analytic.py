# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class Cuenta(models.Model):
    _inherit = 'account.analytic.line'

    category = fields.Char(
        related='product_id.categ_id.name',
        string="Category",
        store=True,
    )
    department = fields.Char(
        store=True,
    )

    motivo = fields.Char(
        String="Motivo",
        store=True,
    )


