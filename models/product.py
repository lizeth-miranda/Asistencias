# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class pro(models.Model):
    _inherit = 'product.template'

    _sql_constraints = [
        ('refer_uniq', 'unique (default_Code)',
         "La referencia interna que está tratando de registrar, ya existe!"),
    ]
