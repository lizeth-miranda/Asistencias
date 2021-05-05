# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import fields, models, api


class empl(models.Model):
    _inherit = 'hr.employee'

    salary = fields.Monetary(
        string="Salario",
    )

    cost_day = fields.Monetary(
        help="Costo/Día",
        string="Costo/Día",
    )
    costo_dayCS = fields.Monetary(
        string="Costo Carga Social x Día",
    )

    timesheet_cost = fields.Monetary(
        'Costo por Hora'
    )
    cost_extra = fields.Monetary(
        help="Costo Extra ",
        string="Costo Extra",
    )
    cost_default = fields.Monetary(
        help="cost per absence",
        string="Costo/Falta",
    )
    cuenta = fields.Char('Cuenta De Depósito',)
    clabe = fields.Char('CLABE Interbancaria',)
    banco = fields.Many2one(comodel_name="res.bank", string="Banco",)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
    )

    # total_hours = fields.Float(
    #     related="last_attendance_id.total_hours"
    # )
    horas_lab = fields.Float(string="Horas laborales", required=True)
    hours = fields.Float(
        string="Horas Sábado",
    )
    normal = fields.Boolean(
        String="Horario normal",
    )
