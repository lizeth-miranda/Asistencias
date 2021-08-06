# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import fields, models, api


class quality(models.Model):
    _inherit = 'quality.alert'

    active = fields.Boolean(string="Archivado", default=True,)
