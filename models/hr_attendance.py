# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError
import time
import pytz


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
    check_out = fields.Datetime(
        string="Check Out", default=fields.Datetime.now,)
    fecha = fields.Date(string="Fecha",
                        required=True, readonly=False, default=fields.Date.today)
    hora_in = fields.Float(string="Entrada",)
    hora_out = fields.Float(string="Salida",)

    codigo_empleado = fields.Char(
        related="employee_id.cod_emp",
        string="Código empleado",
    )
    sueldo_semanal = fields.Monetary(
        related="employee_id.salary",
        string="Sueldo Semanal",
    )
    cost_day = fields.Monetary(
        related='employee_id.cost_day',
        string="Costo/Día",
    )
    timesheet_cost = fields.Monetary(
        related='employee_id.timesheet_cost',
        string="Costo/Hora",
    )
    cost_extra = fields.Monetary(
        related='employee_id.cost_extra',
        string="Costo Extra",
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
        # related="employee_id.resource_calendar_id.attendance_ids.hours",
        string="Horas Laborales",
    )
    # hrs_lab_in = fields.Float(related="employee_id.horas_lab_in",)

    department = fields.Char(
        related="employee_id.department_id.name",
        string="Departamento",
    )
    # Date = fields.Date(
    #     compute='_Date',
    #     store=True,
    # )
    # total = fields.Char(
    #     compute='_total',
    # )
    day = fields.Integer(
        compute='_day',
    )
    hours_sat = fields.Float(
        related="employee_id.hours",
    )
    normal = fields.Boolean(
        related="employee_id.normal"
    )
    mitad = fields.Float(
        compute="_mitad"
    )
    total_hours = fields.Float(
        compute='_total_hours',
        # store=True,
        string="Horas Totales"
    )

    # total_extra = fields.Monetary(
    #     compute='_total_extra',
    #     store=True,
    #     string="Total Extra",
    # )
    # hours_whitout_extra = fields.Float(
    #     compute='_hours_whitout_extra',
    #     store=True,)
    horas_trab = fields.Float(
        string="Horas Trabajadas", compute="horas_traba",)

    # total_inci = fields.Monetary(
    #     compute="compute_horas_traba", string="Total Incidencia",)
# obtener usuario actual
    user_id = fields.Many2one('res.users', string='Residente',
                              required=False, readonly=True, default=lambda self: self.env.user.id)
    tipo_resid = fields.Selection(related="user_id.tipo_resi")

    @ api.depends('hours')
    def _mitad(self):
        for record in self:
            if record.day == 5:
                record.mitad = record.hours_sat/2
            else:
                record.mitad = record.hours / 2

    @ api.depends('fecha')
    def _day(self):
        for record in self:
            record.day = record.fecha.weekday()

    # @ api.depends('check_in')
    # def _Date(self):
    #     for record in self:
    #         dt = record.check_in
    #         date = fields.Datetime.to_string(fields.Datetime.context_timestamp(
    #             self, fields.Datetime.from_string(dt)))[:10]
    #         record.Date = date

    # suma los valores de un campo de todos sus registros
    @api.depends('hora_in', 'hora_out')
    def horas_traba(self):
        for rec in self:
            if rec.hora_out:
                rec.horas_trab = rec.hora_out-rec.hora_in
            else:
                rec.horas_trab = False

    @ api.depends('horas_trab')
    def _total_hours(self):
        for attendance in self:
            attendance.total_hours = sum(self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.name),
                # ('account_ids', '=', attendance.account_ids.id),
                ('fecha', '=', attendance.fecha),
            ]).mapped('horas_trab'))

    @ api.depends('total_hours')
    def _hours_extra(self):
        for attendance in self:
            if attendance.day != 5 and attendance.total_hours >= attendance.hours:
                attendance.hours_extra = (
                    attendance.total_hours-attendance.hours)//1

            elif attendance.day == 5 and attendance.tipo_resid == 'planta':
                attendance.hours_extra = attendance.total_hours

            elif attendance.day == 5 and attendance.tipo_resid == 'obra':
                attendance.hours_extra = attendance.total_hours-attendance.hours_sat

            elif attendance.day == 6:
                attendance.hours_extra = attendance.total_hours

    # @ api.depends('hora_in', 'hora_out')
    # def _hours_whitout_extra(self):
    #     for record in self:
    #         if record.hours_extra > 0:
    #             record.hours_whitout_extra = record.horas_trab - record.hours_extra

    # @ api.depends('hours_extra', 'cost_extra')
    # def _total_extra(self):
    #     for record in self:
    #         record.total_extra = record.hours_extra * record.cost_extra

    # @ api.depends('hora_in', 'hora_out')
    # def compute_cost_total(self):
    #     for record in self:
    #         if record.day != 5:
    #             total2 = (record.timesheet_cost) * (record.hrs_lab_in)
    #             record.cost_total = (total2 + record.total_extra) * -1

            # elif record.hours_extra > 0:
            #     total2 = (record.timesheet_cost * record.hours_whitout_extra)
            #     record.cost_total = (total2 + record.total_extra) * -1

            # elif record.day == 5 and record.normal == True:
            #     record.cost_total = (record.cost_extra *
            #                          record.horas_trab) * -1

            # elif record.day == 6:
            #     record.cost_total = (record.cost_extra *
            #                          record.hrs_lab_in) * -1

            # elif record.day == 5 and record.normal == False:
            #     total1 = record.timesheet_cost * record.hrs_lab_in
            #     record.cost_total = (total1 + record.total_extra) * -1

    @ api.constrains('hora_in')
    def _take(self):
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('fecha', '=', attendance.fecha),
                ('hora_in', '=', attendance.hora_in),
                ('id', '!=', attendance.id),
            ], order='hora_in desc', limit=1)
            if last_attendance_before_check_in:
                raise exceptions.ValidationError(_("No se puede crear una nueva asistencia para el registro %(empl_name)s") % {
                    'empl_name': attendance.employee_id.name,
                    # 'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
                })

    # create a new line, as none existed before

    @ api.constrains('day')
    def nomina_line(self):
        for record in self:
            nomina_line = self.env['nomina.line'].search_count([
                ('employee_id.id', '=', record.employee_id.id),
                ('project', '=', record.account_ids.id),
                ('fecha', '=', record.fecha),
                ('check_in', '=', record.hora_in),
                ('check_out', '=', record.hora_out),
            ])
            print(nomina_line)
            if nomina_line > 0:
                raise ValidationError(_("Los registros ya existen"))

            elif not nomina_line:
                self.env['nomina.line'].create({
                    'employee_id': record.employee_id.id,
                    'department': record.department,
                    'project': record.account_ids.id,
                    'fecha': record.fecha,
                    'check_in': record.hora_in,
                    'check_out': record.hora_out,
                    'worked_hours': record.horas_trab,
                    # 'puesto_trabajo': self.puesto_trabajo,
                    # 'codigo_empleado': record.codigo_empleado,
                    'sueldo_semanal': record.sueldo_semanal,
                    'cost_day': record.cost_day,
                    'cost_hour': record.timesheet_cost,
                    'extra_cost': record.cost_extra,
                    'hours_extra': record.hours_extra,
                    'us_id': record.user_id.name,
                    'type_resi': record.tipo_resid,
                    # 'total_extra': record.total_extra,
                    # 'cost_total': record.cost_total,
                    # 'total_inci': record.total_inci,

                })
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Registro Exitoso',
                    'type': 'rainbow_man',
                }
            }
              
    # if our attendance is "open" (no check_out), we verify there is no other "open" attendance

    # @ api.constrains('check_in', 'check_out', 'employee_id')
    # def _check_validity(self):

    #     for attendance in self:
    #         if not attendance.check_out:

    #             no_check_out_attendances = self.env['hr.attendance'].search([
    #                 ('employee_id', '=', attendance.employee_id.id),
    #                 ('check_out', '=', False),
    #                 ('id', '!=', attendance.id),
    #             ], order='check_in desc', limit=1)
    #             if no_check_out_attendances:
    #                 raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
    #                     'empl_name': attendance.employee_id.name,
    #                     'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
    #                 })

