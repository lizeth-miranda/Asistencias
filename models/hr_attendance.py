# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError

class hr_atten(models.Model):
    _inherit = 'hr.attendance'

    account_ids = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Proyecto",
    )
    # puesto_trabajo = fields.Many2one(
    #     related="employee_id.department_id",
    #     string="Puesto",
    # )
    # check_in = fields.Datetime(
    #     default=fields.Datetime.now,)
    # check_out = fields.Datetime(
    #     string="Check Out", default=fields.Datetime.now,)
    fecha = fields.Date(string="Fecha",
                        required=True, readonly=False, default=fields.Date.today)
    hora_in = fields.Float(string="Entrada",)
    hora_out = fields.Float(string="Salida",)

    codigo_empleado = fields.Char(
        related="employee_id.cod_emp",
        string="Código empleado",
    )
    
    currency_id = fields.Many2one(
        related='employee_id.currency_id',
    )
    cost_total = fields.Monetary(
        compute='compute_cost_total',
        store=True,
        string="Costo Total"
    )
    hours_extra = fields.Float(
        compute='_hours_extra',
        string="Horas Extras",
        store=True,
    )

    dia = fields.Selection(
        related="employee_id.resource_calendar_id.attendance_ids.dayofweek",
    )
    hours = fields.Float(
        related="employee_id.horas_lab",
        string="Horas Laborales",
    )
    department = fields.Char(
        related="employee_id.department_id.name",
        string="Departamento",
    )

    day = fields.Integer(
        compute='_day',
    )
    hours_sat = fields.Float(
        related="employee_id.hours",
    )
    normal = fields.Boolean(
        related="employee_id.normal"
    )
    
    total_hours = fields.Float(
        compute='_total_hours',
        # store=True,
        string="Horas Totales"
    )


    comen = fields.Char(string="Comentarios",)

    user_id = fields.Many2one('res.users', string='Residente',
                              required=False, readonly=True, default=lambda self: self.env.user.id)
    tipo_resid = fields.Selection(related="user_id.tipo_resi")

    asistencia = fields.Boolean(default=True, string="asistencia",)

    block_lines = fields.Selection([('done', 'Registrado')], string='Estado', )

  
    @ api.depends('fecha')
    def _day(self):
        for record in self:
            record.day = record.fecha.weekday()


    @ api.depends('fecha')
    def _total_hours(self):
        for attendance in self:
            attendance.total_hours = sum(self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.name),
                # ('account_ids', '=', attendance.account_ids.id),
                ('fecha', '=', attendance.fecha),
            ]).mapped('worked_hours'))

    @ api.depends('total_hours')
    def _hours_extra(self):
        for attendance in self:
            if attendance.day != 5 and attendance.total_hours >= attendance.hours:
                attendance.hours_extra = (
                    attendance.total_hours-attendance.hours)//1

            elif attendance.day == 5 and attendance.tipo_resid == 'planta':
                attendance.hours_extra = attendance.total_hours

            elif attendance.day == 5 and attendance.tipo_resid == 'obra':
                attendance.hours_extra = (
                    attendance.total_hours-attendance.hours_sat) // 1

            elif attendance.day == 6:
                attendance.hours_extra = attendance.total_hours


    # create a new line, as none existed before

    @ api.constrains('fechaA')
    def nomina_line(self):
        for record in self:
            nomina_line = self.env['nomina.line'].search_count([
                ('employee_id.id', '=', record.employee_id.id),
                ('project', '=', record.account_ids.id),
                ('fechaA', '=', record.fecha),
                ('check_in', '=', record.check_in),
                ('check_out', '=', record.check_out),
            ])
            print(nomina_line)
            if nomina_line > 0:
                raise ValidationError(
                    _("Una o varias asistencias ya existen registradas "))

            elif not nomina_line:
                record.env['nomina.line'].create({
                    'employee_id': record.employee_id.id,
                    'department': record.department,
                    'project': record.account_ids.id,
                    'fechaA': record.fecha,
                    'check_in': record.check_in,
                    'check_out': record.check_out,
                    'worked_hours': record.worked_hours,
                    'notas': record.comen,
                    'us_id': record.user_id.name,
                    'type_resi': record.tipo_resid,
                    'asis': record.asistencia,
                })
            record.block_lines = 'done'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Registro Exitoso',
                'type': 'rainbow_man',
            }
        }
