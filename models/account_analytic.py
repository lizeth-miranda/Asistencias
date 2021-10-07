# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class Cuenta(models.Model):
    _inherit = 'account.analytic.line'

    cate = fields.Char(
        related='product_id.categ_id.name',
        store=True,
    )
    job_pos = fields.Char(
        store=True,
    )

    motivo = fields.Char(
        String="Motivo",
        store=True,
    )
    nom = fields.Boolean(string="nomina",)
    
  

