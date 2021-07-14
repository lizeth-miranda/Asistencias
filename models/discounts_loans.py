# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models


class DiscountsLoans(models.Model):
    _name = 'discounts.loans'
    _description = 'Discount Loans'

    employee_id = fields.Many2one(
        'discount.employee', ondelete='cascade', required=True,)

    type_discount = fields.Selection([
        ('pre_per', 'Préstamo Personal'),
        ('desc_herr', 'Desc.EPP Herramienta'),
        ('otr_des', 'Otros Descuentos'),
    ], string='Tipo de Descuento',)

    fecha = fields.Datetime(
        'Fecha', required=False, readonly=False, default=fields.Datetime.now)
    fecha2 = fields.Date(compute="compute_fecha2",)

    fecha_actual = fields.Datetime(
        'Fecha_actual', readonly=False, compute="compute_fechaActual",)
    fecha_antes = fields.Datetime(compute="compute_fecha_antes",)
    total = fields.Monetary(string="Total",)
    #total2 = fields.Monetary(compute="compute_total2",)
    # deposito = fields.Boolean(
    #     string="Depósito", compute="dep_false", inverse="inverse_dep_false", store=True,)
    semanas = fields.Float(string="Semanas",)
    abono = fields.Monetary(
        string="Abono",
        compute="compute_abono", store=True, )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
    )

    fecha_pp = fields.Datetime(
        compute="compute_fecha_pp", string="Fecha Primer Pago",)
    onlyfecha_pp = fields.Date(compute="compute_onlyfecha_pp")
    fecha_up = fields.Datetime(
        compute="compute_fecha_up", string="Fecha Final de pago",)

    fecha_back_ultima = fields.Datetime(
        compute="compute_fecha_back_ultima",)

    num_pago = fields.Integer(
        string="# Pago", compute="compute_num_pago", store=True,)
    saldo = fields.Monetary(
        string="Saldo", compute="compute_saldo", store=True,)

    suma_abonopp = fields.Monetary(
        string="Suma Prestamos personal", compute="compute_sum_abono",)
    suma_descEpp = fields.Monetary(
        string="Suma Desc.EPP", compute="compute_suma_descEpp",)
    suma_otros_desc = fields.Monetary(
        string="Suma Otros Descuentos", compute="compute_suma_otrosDesc",)

    dep = fields.Monetary(string="Deposito",)

    @api.depends('fecha')
    def compute_fecha_antes(self):
        for record in self:
            if record.fecha:
                record.fecha_antes = record.fecha - timedelta(weeks=1)
                return fields.Date.context_today(self, timestamp=record.fecha_antes)

    @api.depends('type_discount')
    def compute_fechaActual(self):
        for record in self:
            record.fecha_actual = fields.datetime.now()

    @ api.depends('fecha')
    def compute_fecha2(self):
        for record in self:
            f1 = record.fecha
            date = fields.Datetime.to_string(fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(f1)))[:10]
            record.fecha2 = date

    # esta función le suma dias,horas, minutos, etc a un campo Datetime**
    @api.depends('fecha')
    def compute_fecha_pp(self):
        for record in self:
            if record.fecha:
                record.fecha_pp = record.fecha + timedelta(weeks=1)
                return fields.Date.context_today(self, timestamp=record.fecha_pp)

    # calcular solo fecha de el primer pago

    @ api.depends('fecha_pp')
    def compute_onlyfecha_pp(self):
        for record in self:
            f2 = record.fecha_pp
            datee = fields.Datetime.to_string(fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(f2)))[:10]
            record.onlyfecha_pp = datee

    # esta función le suma dias,horas, minutos, etc a un campo Datetime**
    @api.depends('semanas')
    def compute_fecha_up(self):
        for record in self:
            record.fecha_up = record.fecha + timedelta(weeks=(record.semanas))
            return fields.Date.context_today(self, timestamp=record.fecha_up)

    @api.depends('semanas')
    def compute_fecha_back_ultima(self):
        for record in self:
            record.fecha_back_ultima = record.fecha_antes + \
                timedelta(weeks=(record.semanas))
            return fields.Date.context_today(self, timestamp=record.fecha_back_ultima)

    @api.depends('semanas')
    def compute_abono(self):
        for record in self:
            if not record.semanas:
                record.abono = 0.0
            else:
                record.abono = record.total / record.semanas

    @api.depends('fecha_actual')
    def compute_num_pago(self):
        for rec in self:
            if rec.fecha_actual and rec.type_discount in ['pre_per', 'Préstamo Personal']:
                r1 = (rec.fecha_up - rec.fecha_actual).days
                r2 = r1 / 7
                rec.resta2 = rec.semanas - r2
                rec.num_pago = rec.resta2
            else:
                r1 = (rec.fecha_back_ultima - rec.fecha_actual).days
                r2 = r1 / 7
                rec.resta2 = rec.semanas - r2
                rec.num_pago = rec.resta2

    @api.depends('num_pago')
    def compute_saldo(self):
        for rec in self:
            if rec.num_pago < rec.semanas:
                rec.saldo = rec.total - \
                    (rec.abono * rec.num_pago)
            else:
                rec.saldo = False

    @api.depends('abono')
    def compute_sum_abono(self):
        for record in self:
            record.suma_abonopp = sum(self.env['discounts.loans'].search([
                ('employee_id', '=', record.employee_id.id),
                ('type_discount', '=', 'pre_per'),
                ('num_pago', '>', 0),
                ('saldo', '>', 0),
            ]).mapped('abono'))

    @api.depends('abono')
    def compute_suma_descEpp(self):
        for record in self:
            record.suma_descEpp = sum(self.env['discounts.loans'].search([
                ('employee_id', '=', record.employee_id.id),
                ('type_discount', '=', 'desc_herr'),
                ('num_pago', '>', 0),
                ('saldo', '>', 0),
            ]).mapped('abono'))

    @api.depends('abono')
    def compute_suma_otrosDesc(self):
        for record in self:
            record.suma_otros_desc = sum(self.env['discounts.loans'].search([
                ('employee_id', '=', record.employee_id.id),
                ('type_discount', '=', 'otr_des'),
                ('num_pago', '>', 0),
                ('saldo', '>', 0),
            ]).mapped('abono'))

    @api.onchange('num_pago')
    def deposito_false(self):
        for rec in self:
            if rec.total == rec.saldo and rec.type_discount in ['pre_per', 'Préstamo Personal']:
                rec.dep = rec.total
            elif rec.total != rec.saldo:
                rec.dep = False

