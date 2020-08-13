# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class Users(models.Model):
    _inherit = 'res.users'

    project_id = fields.One2many(
        comodel_name='account.analytic.account',
        inverse_name='users',
        string="Proyectos",
    )
