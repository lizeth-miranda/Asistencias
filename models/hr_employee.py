# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import fields, models, api


class Costos(models.Model):
    _inherit = 'hr.employee'

    salary = fields.Monetary(
        required=True,
        string="Salary",
    )

    cost_day = fields.Monetary(
        required=True,
        help="Cost per Day",
    )

    timesheet_cost = fields.Monetary(
        'Timesheet Cost',
    )
    cost_extra = fields.Monetary(
        required=True,
        help="extra cost ",
    )
    cost_default = fields.Monetary(
        required=True,
        help="cost per absence",
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
    )
    # total_hours = fields.Float(
    #     related="last_attendance_id.total_hours"
    # )
    hours = fields.Float(
        required=True,
        string="Saturday Hours",
    )
    normal = fields.Boolean(
        required=True,
        String="Horario normal",
    )

