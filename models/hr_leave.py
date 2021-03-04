# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class hr_lea(models.Model):
    _inherit = 'hr.leave'

    account_ids = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Project",
        required=True,
    )
    cost_day = fields.Monetary(
        related='employee_id.cost_day',
        string="Cost day",
    )
    cost_default = fields.Monetary(
        compute='_cost_default',
        string="Costo/Falta",
    )
    currency_id = fields.Many2one(
        related='employee_id.currency_id',
    )
    pues_tra = fields.Char(
        related="employee_id.department_id.name",
        string="Puesto de Trabajo",
    )

    @api.depends('number_of_days')
    def _cost_default(self):
        for record in self:
            record.cost_default = (
                record.cost_day * record.number_of_days) * -1

    def action_approve(self):
        res = super(hr_lea, self).action_approve()
        self.env['account.analytic.line'].create({
            'date': self.request_date_from,
            'name': self.employee_id.name,
            'job_pos': self.depa,
            'account_id': self.account_ids.id,
            'amount': self.cost_default,
        })
        return res

