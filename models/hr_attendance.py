# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models, exceptions, _
from datetime import datetime
from odoo.exceptions import ValidationError
# from date import date


class Cuenta(models.Model):
    _inherit = 'hr.attendance'

    account_ids = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Project",
        required=True,
    )
    cost_day = fields.Monetary(
        related='employee_id.cost_day',
    )
    timesheet_cost = fields.Monetary(
        related='employee_id.timesheet_cost',
        string="Cost Hour",
    )
    cost_extra = fields.Monetary(
        related='employee_id.cost_extra',
        string="Extra Cost",
    )
    currency_id = fields.Many2one(
        related='employee_id.currency_id',
    )
    cost_total = fields.Monetary(
        compute='_cost_total',
    )

    dia = fields.Selection(
        related="employee_id.resource_calendar_id.attendance_ids.dayofweek",
    )
    hours = fields.Float(
        related="employee_id.resource_calendar_id.attendance_ids.hours",
    )

    department = fields.Char(
        related="employee_id.department_id.name",
    )
    Date = fields.Date(
        compute='_Date',
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
            record.Date = record.check_in

    @ api.depends('timesheet_cost', 'check_out')
    def _cost_total(self):
        for record in self:
            if record.day == 5 and record.normal == False:
                record.cost_total = record.cost_extra * record.worked_hours

            elif record.day == 5 and record.normal == True:
                record.cost_total = record.timesheet_cost * record.hours_sat

            elif record.day != 5 and record.worked_hours >= record.hours:
                record.cost_total = record.timesheet_cost * record.hours

            elif record.day != 5 and record.worked_hours > record.mitad:
                record.cost_total = record.timesheet_cost * record.mitad

            elif record.day != 5 and record.worked_hours < record.mitad:
                record.cost_total = record.timesheet_cost * record.mitad

    # create a new line, as none existed before
    @api.constrains('check_in.weekday()')
    def _account_analytic(self):
        for record in self:
            record.account_analytic = self.env['account.analytic.line'].search([
                ('date', '=', self.check_in),
                ('name', '=', self.employee_id.name),
                ('department', '=', self.department),
                ('work_hours', '=', self.worked_hours),
                ('cost_extra', '=', self.cost_extra),
                ('hours_sat', '=', self.hours_sat),
                ('day', '=', self.day),
                ('hours', '=', self.hours),
                ('normal', '=', self.normal),
                ('account_id', '=', self.account_ids.id),
                ('amount', '=', self.cost_total),
            ])
            if record.account_analytic:
                raise ValidationError(_("Los registros ya existen"))

            elif not record.account_analytic:
                self.env['account.analytic.line'].create({
                    'date': self.check_in,
                    'name': self.employee_id.name,
                    'department': self.department,
                    'work_hours': self.worked_hours,
                    'cost_extra': self.cost_extra,
                    'hours_sat': self.hours_sat,
                    'day': self.day,
                    'hours': self.hours,
                    'normal': self.normal,
                    'account_id': self.account_ids.id,
                    'amount': self.cost_total,
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

