# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models, _


class hr_lea(models.Model):
    _inherit = 'hr.leave.type'

    tipo_inci = fields.Selection([('falta', 'FALTA'),
                                  ('asis', 'ASISTENCIA')], string='Tipo de Incidencia', )
