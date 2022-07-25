# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class Cuenta(models.Model):
    _inherit = 'account.analytic.line'

    categ_padre = fields.Char(
        related='product_id.categ_id.display_name',
        store=True,
        string="Categoria de Producto",
    )
     # job_pos = fields.Char(
    #     store=True,
    #     string="Puesto de Trabajo",
    # )

    # motivo = fields.Char(
    #     String="Motivo",
    #     store=True,
    # )
    # nom = fields.Boolean(string="nomina",)
    
  

