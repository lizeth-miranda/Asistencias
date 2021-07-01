  # -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import fields, models, api
from datetime import datetime, timedelta


class empl(models.Model):
    _inherit = 'hr.employee'

    salary = fields.Monetary(
        string="Salario",
    )

    cod_emp = fields.Char(string="Código Empleado",)
    fecha_ingreso = fields.Date(string="Fecha de Ingreso",)
    afiliacion_imss = fields.Char(string="Afiliación IMSS",)

    cost_day = fields.Monetary(
        help="sueldo semanal/6",
        string="Costo/Día",
    )
    costo_dayCS = fields.Monetary(
        string="Carga Social por Día",
    )

    timesheet_cost = fields.Monetary(
        'Costo por Hora'
    )
    cost_extra = fields.Monetary(
        help="Costo Extra/hr",
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
    horas_lab = fields.Float(string="Horas laborales",
                             help="Horales Laborales Control Obra")
    horas_lab_in = fields.Float(
        string="Horas Laborales CI", help="Horales Laborales Control Nómina",)
    hours = fields.Float(
        string="Horas Sábado",
    )
    normal = fields.Boolean(
        String="Horario normal",
    )

    credito_info = fields.Monetary(string="Crédito Infonavit",)
    credito_fona = fields.Monetary(string="Crédito Fonacot",)
    bono = fields.Monetary(
        string="Bono Fijo",
    )

    empresa = fields.Selection([
        ('enterprise', 'PCA Grupo Prefabricador'),
        ('enterprise2', 'DEMSA'),
    ], string="Empresa",)

    # calcular prestamos
    fecha_actual = fields.Datetime(
        string="Fecha Préstamo", default=fields.Datetime.now, readonly=False,)
    total_prestamo = fields.Monetary(string="Préstamo",)
    semanas = fields.Float(string="Semanas",)
    abono = fields.Monetary(
        string="Abono", compute="compute_abono", store=True, )
    fecha_pp = fields.Datetime(
        compute="compute_fecha_pp", string="Fecha Primer Pago",)
    onlyfecha_pp = fields.Date(compute="compute_onlyfecha_pp")
    fecha_up = fields.Datetime(
        compute="compute_fecha_up", string="Fecha Final de pago",)

    # calcular solo fecha de el primer pago
    @ api.depends('fecha_pp')
    def compute_onlyfecha_pp(self):
        for record in self:
            f1 = record.fecha_pp
            date = fields.Datetime.to_string(fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(f1)))[:10]
            record.onlyfecha_pp = date

    @ api.depends('semanas')
    def compute_abono(self):
        for record in self:
            if not record.semanas:
                record.abono = 0.0
            else:
                record.abono = record.total_prestamo / record.semanas

    # esta función le suma dias,horas, minutos, etc a un campo Datetime**
    @ api.depends('semanas')
    def compute_fecha_pp(self):
        self.fecha_pp = self.fecha_actual + timedelta(weeks=1)
        return fields.Date.context_today(self, timestamp=self.fecha_pp)

    # esta función le suma dias,horas, minutos, etc a un campo Datetime**
    @ api.depends('semanas')
    def compute_fecha_up(self):
        self.fecha_up = self.fecha_actual + timedelta(weeks=(self.semanas))
        return fields.Date.context_today(self, timestamp=self.fecha_up)

    # Descuentos personales
    fecha_descuento = fields.Datetime(
        string="Fecha", default=fields.Datetime.now, readonly=False,)
    descuento = fields.Monetary(string="Total material a cobro",)
    rango = fields.Float(string="Num Semanas",)
    pago = fields.Monetary(string="Cantidad a Descontar", compute="compute_pago", store=True,)
    fecha_pd = fields.Datetime(
        compute="compute_fecha_pd", string="Fecha Primer Descuento",)
    onlyfecha_pd = fields.Date(compute="compute_onlyfecha_pd")
    fecha_final = fields.Datetime(
        compute="compute_fecha_final", string="Fecha Final",)
    desc = fields.Text(string="Descripción",)

    # calcular solo fecha de el primer pago
    @ api.depends('fecha_pd')
    def compute_onlyfecha_pd(self):
        for record in self:
            f2 = record.fecha_pd
            date2 = fields.Datetime.to_string(fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(f2)))[:10]
            record.onlyfecha_pd = date2

    @api.depends('rango')
    def compute_pago(self):
        for record in self:
            if not record.rango:
                record.pago = 0.0
            else:
                record.pago = record.descuento / record.rango

    @api.model  # esta función le suma dias,horas, minutos, etc a un campo Datetime**
    def compute_fecha_pd(self):
        self.fecha_pd = self.fecha_descuento + timedelta(weeks=1)
        return fields.Date.context_today(self, timestamp=self.fecha_pd)

    @api.depends('rango')
    def compute_fecha_final(self):
        self.fecha_final = self.fecha_descuento + timedelta(weeks=(self.rango))
        return fields.Date.context_today(self, timestamp=self.fecha_final)
