# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class Nomina(models.Model):
    _name = "nomina.line"
    _description = 'Registro de Nomina'

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Employee",
        readonly=True,
    )
    department = fields.Char(
        string="Department",
        readonly=True,
    )
    project = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Project",
        readonly=True,
    )
    check_in = fields.Datetime(
        string="Check In",
    )
    check_out = fields.Datetime(
        string="Check Out",
    )
    worked_hours = fields.Float(
        string="Worked Hours",
        compute='_compute_worked_hours',
        store=True,
    )
    hours_extra = fields.Float(
        string="Hours Extra",
        # compute='_hours_extra',
        # store=True,
    )
    total_extra = fields.Monetary(
        string="Total Extra",
        compute='_total_extra',
        store=True,
        readonly=True,
    )
    cost_total = fields.Monetary(
        string="Total Cost",
        compute='_cost_total',
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        related='employee_id.currency_id',
    )
    cost_day = fields.Monetary(
        string="Cost Day",
        store=True,
        readonly=True,
    )
    cost_hour = fields.Monetary(
        string="Cost Hour",
        readonly=True,
    )
    extra_cost = fields.Monetary(
        string="Extra Cost",
        readonly=True,
    )
    hours = fields.Float(
        related="employee_id.resource_calendar_id.attendance_ids.hours",
    )
    day = fields.Integer(
        compute='_day',
    )
    normal = fields.Boolean(
        related="employee_id.normal",
        string="Horario Normal",
    )
    hours_sat = fields.Float(
        related="employee_id.hours",
    )
    Date = fields.Date(
        compute='_Date',
        store=True,
    )
    # total_hours = fields.Float(
    #     compute='_total_hours',
    #     # store=True,
    # )

    @api.depends('check_in')
    def _day(self):
        for record in self:
            record.day = record.check_in.weekday()

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False

    @api.depends('hours_extra')
    def _total_extra(self):
        for record in self:
            if record.hours_extra == 0:
                record.total_extra = False
            else:
                record.total_extra = record.hours_extra * record.extra_cost

    @api.depends('worked_hours', 'hours_extra')
    def _cost_total(self):
        for record in self:
            if record.normal == True and record.day == 5:
                t1 = (record.worked_hours * record.cost_hour)
                self.cost_total = t1 + self.total_extra

            elif record.normal == False and record.day == 5:
                record.cost_total = record.total_extra

            elif record.day != 5:
                t0 = record.worked_hours-record.hours_extra
                t1 = (t0 * record.cost_hour)
                record.cost_total = (t1 + record.total_extra)*-1

     # create a new line, as none existed before

    @api.constrains('check_in.weekday()')
    def _account_line(self):
        for record in self:
            record.account_line = self.env['account.analytic.line'].search_count([
                ('date', '=', self.check_in),
                ('name', '=', self.employee_id.name),
                ('department', '=', self.department),
                ('account_id', '=', self.project.id),
                ('amount', '=', self.cost_total),
            ])
            if record.account_line > 0:
                raise ValidationError(_("Los registros ya existen"))

            elif not record.account_line:
                self.env['account.analytic.line'].create({
                    'date': self.check_in,
                    'name': self.employee_id.name,
                    'department': self.department,
                    'account_id': self.project.id,
                    'amount': self.cost_total,
                })
