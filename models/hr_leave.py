# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class hr_lea(models.Model):
    _inherit = 'hr.leave'

    account_ids = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Obra",
        required=True,
    )
    cost_day = fields.Monetary(
        related='employee_id.cost_day',
        string="Cost day",
    )

    currency_id = fields.Many2one(
        related='employee_id.currency_id',
    )
    pues_tra = fields.Char(
        related="employee_id.department_id.name",
        string="Puesto de Trabajo",
    )
    num_emp = fields.Char(related="employee_id.cod_emp",)

    leavee = fields.Boolean(
        string="Falta", default=True,
    )

    def action_approve(self):
        res = super(hr_lea, self).action_approve()
        self.env['nomina.line'].create({
            'employee_id': self.employee_id.id,
            'codigo_empleado': self.num_emp,
            'project': self.account_ids.id,
            'department': self.pues_tra,
            'fecha': self.request_date_from,
            'inci': self.holiday_status_id.name,
            'leavee': self.leavee,
            # 'total_inci': self.cost_default,
        })
        return res
