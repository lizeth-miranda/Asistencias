# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class Account(models.Model):
    _inherit = 'account.analytic.account'

    users = fields.Many2one(
        comodel_name="res.users",
        ondelete='cascade',
        string="Residente",
    )
    
    userss = fields.Many2many('res.users', string='Residentes',)
  
