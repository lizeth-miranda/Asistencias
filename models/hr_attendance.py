# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError
# import time
# import pytz


class hr_atten(models.Model):
    _inherit = 'hr.attendance'

    account_ids = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Proyecto",
    )
    fecha = fields.Date(string="Fecha Registro",
                        required=True, readonly=False, default=fields.Date.today)
    Date = fields.Date(
        compute='_Date',
        store=True,)

    codigo_empleado = fields.Char(
        related="employee_id.pin",
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
    tipo_resid = fields.Selection(related="user_id.tipo_resi",)
    tipo_empl = fields.Selection(related="employee_id.tipo_emp",)

    asistencia = fields.Boolean(default=True, string="asistencia",)

    block_lines = fields.Selection([('done', 'Registrado')], string='Estado', )
    tem = fields.Float(string="Temperatura",)

    @ api.depends('Date')
    def _day(self):
        for record in self:
            record.day = record.Date.weekday()
    # fecha para agrupar las horas totales de los empleados con la fecha de la
    # asitencia y no la de la fecha registro

    @api.depends('check_in')
    def _Date(self):
        for record in self:
            dt = record.check_in
            date = fields.Datetime.to_string(fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(dt)))[:10]
            record.Date = date

    @ api.depends('Date')
    def _total_hours(self):
        for attendance in self:
            attendance.total_hours = sum(self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.name),
                # ('account_ids', '=', attendance.account_ids.id),
                ('Date', '=', attendance.Date),
            ]).mapped('worked_hours'))

    @ api.depends('check_out')
    def _hours_extra(self):
        for attendance in self:
            if attendance.day != 5 and attendance.total_hours >= attendance.hours and attendance.tipo_empl != 'admin':
                attendance.hours_extra = (
                    attendance.total_hours-attendance.hours)//1

            elif attendance.day == 5 and attendance.tipo_resid == 'planta' and attendance.tipo_empl != 'admin':
                attendance.hours_extra = attendance.total_hours

            elif attendance.day == 5 and attendance.tipo_resid == 'obra' and attendance.tipo_empl != 'admin':
                attendance.hours_extra = (
                    attendance.total_hours-attendance.hours_sat) // 1

            elif attendance.day == 6 and attendance.tipo_empl != 'admin':
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
