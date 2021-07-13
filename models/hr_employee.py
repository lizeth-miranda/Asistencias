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
    
    discounts_ids = fields.One2many(
        comodel_name='discount.employee',
        inverse_name='employee',
    )

    pres_perso = fields.Monetary(
        string="Préstamo Personal", related="discounts_ids.sum_abono",)

    desc_HPP = fields.Monetary(
        string="Dec.EPP", related="discounts_ids.sum_descEPP",)

    otros_desc = fields.Monetary(
        string="Otros Descuentos", related="discounts_ids.sum_otros_desc",)

    depo = fields.Monetary(related="discounts_ids.deposito",)
    
    
   
