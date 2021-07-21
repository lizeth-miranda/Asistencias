# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odo
from odoo import api, fields, models


class DiscountsEmployee(models.Model):
    _name = 'discount.employee'
    _description = 'Discount Employee'
    
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(employee)',
         "EL EMPLEADO QUE INTENTA REGISTRAR YA CUENTA EXISTE"),
    ]

    employee = fields.Many2one(
        comodel_name='hr.employee', string="Empleado", ondelete='set null', index=True,)

    discLoans_ids = fields.One2many(
        comodel_name='discounts.loans',
        inverse_name='employee_id',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
    )
    sum_abono = fields.Monetary(related="discLoans_ids.suma_abonopp")
    sum_descEPP = fields.Monetary(related="discLoans_ids.suma_descEpp")
    sum_otros_desc = fields.Monetary(related="discLoans_ids.suma_otros_desc")

    tipo_desc = fields.Selection(
        string="Tipo Descuento", related="discLoans_ids.type_discount",)

    total_desc = fields.Monetary(
        string="Total", related="discLoans_ids.total",)

    abono = fields.Monetary(string="Abono", related="discLoans_ids.abono",)

    numero_pago = fields.Integer(
        string="Número de pago", related="discLoans_ids.num_pago",)

    saldo = fields.Monetary(string="Saldo", related="discLoans_ids.saldo",)

    deposito = fields.Monetary(string="Déposito", related="discLoans_ids.dep",)
    sem = fields.Integer(string="Semanas", related="discLoans_ids.semanas",)
