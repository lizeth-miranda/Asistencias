# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import fields, models, api


class empl(models.Model):
    _inherit = 'hr.employee'

    _sql_constraints = [
        ('pin_uniq', 'unique (pin)', "EL CODIGO DE EMPLEADO QUE INTENTA REGISTRAR, YA EXISTE!"),
    ]

    salary = fields.Monetary(
        string="Salario",
    )

    cod_emp = fields.Char(string="Código",)
    fecha_ingreso = fields.Date(string="Fecha de Ingreso",)
    afiliacion_imss = fields.Char(string="Afiliación IMSS",)

    cost_day = fields.Monetary(
        help="sueldo semanal/6", string="Costo/Día", compute="compute_costday",)

    costo_dayCS = fields.Monetary(
        string="Carga Social por Día",
    )

    timesheet_cost = fields.Monetary(
        'Costo por Hora', compute="compute_timecost", help="(sueldo/ 6) /8",)
    cost_extra = fields.Monetary(
        help="(sueldo/6) /8 *2",
        string="Costo Extra",
        compute="compute_costExtra",
    )
    cost_extra_bono = fields.Monetary(
        help="(sueldo + bono fijo/6) /8 *2)",
        string="Costo Extra + Bono",
        compute="compute_costExtra_bono",
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

    discounts_ids = fields.One2many(
        comodel_name='discount.employee',
        inverse_name='employee',
    )

    pres_perso = fields.Monetary(
        string="Préstamo Personal", related="discounts_ids.sum_abono",)

    desc_HPP = fields.Monetary(
        string="Desc.EPP", related="discounts_ids.sum_descEPP",)

    otros_desc = fields.Monetary(
        string="Otros Descuentos", related="discounts_ids.sum_otros_desc",)

    depo = fields.Monetary(related="discounts_ids.deposito",)

    fecha_nacimiento = fields.Date(string="Fecha de Nacimiento",)

    active_CEXB = fields.Boolean(string="Activar Costo Extra + Bono",)

    @api.depends('salary')
    def compute_timecost(self):
        for rec in self:
            rec.timesheet_cost = (rec.salary/6) / 8

    @api.depends('salary')
    def compute_costday(self):
        for rec in self:
            rec.cost_day = rec.salary/6

    @api.depends('salary')
    def compute_costExtra(self):
        for rec in self:
            r1 = (rec.salary/6)
            r2 = r1 / 8
            r3 = r2 * 2
            rec.cost_extra = r3

    @api.depends('salary')
    def compute_costExtra_bono(self):
        for rec in self:
            r4 = (rec.salary + rec.bono) / 6
            r5 = r4 / 8
            r6 = r5 * 2
            rec.cost_extra_bono = r6

   
