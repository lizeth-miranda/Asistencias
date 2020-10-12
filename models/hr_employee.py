# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import fields, models, api


class Costos(models.Model):
    _inherit = 'hr.employee'

    salary = fields.Monetary(
        string="Salary",
    )

    cost_day = fields.Monetary(
        help="Cost per Day",
    )

    timesheet_cost = fields.Monetary(
        'Timesheet Cost',
    )
    cost_extra = fields.Monetary(
        help="extra cost ",
    )
    cost_default = fields.Monetary(
        help="cost per absence",
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
    )
    # total_hours = fields.Float(
    #     related="last_attendance_id.total_hours"
    # )
    hours = fields.Float(
        string="Saturday Hours",
    )
    normal = fields.Boolean(
        String="Horario normal",
    )

