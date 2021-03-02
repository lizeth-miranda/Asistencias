# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError
import time
import pytz


class Cuenta(models.Model):
    _inherit = 'hr.attendance'

    account_ids = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Proyecto",
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
        compute='_cost_total',
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
        related="employee_id.resource_calendar_id.attendance_ids.hours",
        string="Horas Laborales",
    )

    department = fields.Char(
        related="employee_id.department_id.name",
        string="Departamento",
    )
    Date = fields.Date(
        compute='_Date',
        store=True,
    )
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

    total_extra = fields.Monetary(
        compute='_total_extra',
        store=True,
        string="Total Extra",
    )
    hours_whitout_extra = fields.Float(
        compute='_hours_whitout_extra',
        store=True,
    )

    @api.depends('hours')
    def _mitad(self):
        for record in self:
            if record.day == 5:
                record.mitad = record.hours_sat/2
            else:
                record.mitad = record.hours / 2

    @api.depends('check_in')
    def _day(self):
        for record in self:
            record.day = record.check_in.weekday()

    @api.depends('check_in')
    def _Date(self):
        for record in self:
            dt = record.check_in
            date = fields.Datetime.to_string(fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(dt)))[:10]
            record.Date = date

    # suma los valores de un campo de todos sus registros
    @api.depends('worked_hours')
    def _total_hours(self):
        for attendance in self:
            attendance.total_hours = sum(self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.name),
                #('account_ids', '=', attendance.account_ids.id),
                ('Date', '=', attendance.Date),
            ]).mapped('worked_hours'))

    @api.depends('total_hours')
    def _hours_extra(self):
        for attendance in self:
            if attendance.total_hours >= attendance.hours:
                attendance.hours_extra = (
                    attendance.total_hours-attendance.hours)

            elif attendance.normal == True and attendance.day == 5 and attendance.total_hours > attendance.hours_sat:
                attendance.hours_extra = (
                    attendance.total_hours - attendance.hours_sat)

            elif attendance.normal == False and attendance.day == 5:
                attendance.hours_extra = attendance.worked_hours

    @ api.depends('check_in', 'check_out')
    def _hours_whitout_extra(self):
        for record in self:
            if record.hours_extra > 0:
                record.hours_whitout_extra = record.worked_hours - record.hours_extra

    @ api.depends('hours_extra', 'cost_extra')
    def _total_extra(self):
        for record in self:
            record.total_extra = record.hours_extra * record.cost_extra

    @ api.depends('check_in', 'check_out')
    def _cost_total(self):
        for record in self:
            if record.hours_extra == 0:
                total2 = (record.timesheet_cost * record.worked_hours)
                record.cost_total = (total2 + record.total_extra) * -1

            elif record.hours_extra > 0:
                total2 = (record.timesheet_cost * record.hours_whitout_extra)
                record.cost_total = (total2 + record.total_extra) * -1

            elif record.day == 5 and record.normal == False:
                record.cost_total = (record.cost_extra *
                                     record.worked_hours) * -1

            elif record.day == 5 and record.normal == True:
                total1 = record.timesheet_cost * record.hours_sat
                record.cost_total = (total1 + record.total_extra) * -1

    @ api.constrains('check_in')
    def _take(self):
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                raise exceptions.ValidationError(_("No se puede crear una nueva asistencia para el registro %(empl_name)s, el empleado ya esta registrado en %(datetime)s") % {
                    'empl_name': attendance.employee_id.name,
                    'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
                })

    # create a new line, as none existed before

    @api.constrains('check_in.weekday()')
    def _nomina_line(self):
        for record in self:
            record.nomina_line = self.env['nomina.line'].search_count([
                ('employee_id', '=', self.employee_id.id),
                ('department', '=', self.department),
                ('project', '=', self.account_ids.id),
                ('check_in', '=', self.check_in),
                ('check_out', '=', self.check_out),
                ('worked_hours', '=', self.worked_hours),
                ('cost_day', '=', self.cost_day),
                ('cost_hour', '=', self.timesheet_cost),
                ('extra_cost', '=', self.cost_extra),
                ('hours_extra', '=', self.hours_extra),
                ('total_extra', '=', self.total_extra),
                ('cost_total', '=', self.cost_total),
                ('normal', '=', self.normal),
            ])
            if record.nomina_line > 0:
                raise ValidationError(_("Los registros ya existen"))

            elif not record.nomina_line:
                self.env['nomina.line'].create({
                    'employee_id': self.employee_id.id,
                    'department': self.department,
                    'project': self.account_ids.id,
                    'check_in': self.check_in,
                    'check_out': self.check_out,
                    'worked_hours': self.worked_hours,
                    'cost_day': self.cost_day,
                    'cost_hour': self.timesheet_cost,
                    'extra_cost': self.cost_extra,
                    'hours_extra': self.hours_extra,
                    'total_extra': self.total_extra,
                    'cost_total': self.cost_total,
                    'normal': self.normal,
                })
    # if our attendance is "open" (no check_out), we verify there is no other "open" attendance

    @ api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):

        for attendance in self:
            if not attendance.check_out:

                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if no_check_out_attendances:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
                    })
