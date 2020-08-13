# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class Cuenta(models.Model):
    _inherit = 'hr.leave'

    account_ids = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Project",
        required=True,
    )
    cost_day = fields.Monetary(
        related='employee_id.cost_day',
    )
    cost_default = fields.Monetary(
        compute='_cost_default',
    )
    currency_id = fields.Many2one(
        related='employee_id.currency_id',
    )

    @api.depends('number_of_days')
    def _cost_default(self):
        for record in self:
            record.cost_default = record.cost_day * record.number_of_days

    def action_approve(self):
        res = super(Cuenta, self).action_approve()
        self.env['account.analytic.line'].create({
            'date': self.request_date_from,
            'name': self.employee_id.name,
            'department': self.holiday_status_id.display_name,
            'account_id': self.account_ids.id,
            'amount': self.cost_default,
        })
        return res
