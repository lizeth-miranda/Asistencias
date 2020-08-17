# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class Cuenta(models.Model):
    _inherit = 'account.analytic.line'

    category = fields.Char(
        related='product_id.categ_id.name',
        string="Category",
        store=True,
    )
    department = fields.Char(
        store=True,
    )
    work_hours = fields.Float(
        string="Work Hours"
    )
    total_extra = fields.Monetary(
        compute='_total_extra',
        store=True,
        string="Total Extra",
    )
    cost_extra = fields.Monetary(
        string="Cost Extra",
    )
    hours = fields.Float(
        string="Hours",
    )
    mitad = fields.Float(
        compute="_mitad"
    )
    hours_extra = fields.Float(
        compute='_hours_extra',
        string="Hours Extra ",
        store=True,
    )
    hours_sat = fields.Float(

    )
    day = fields.Integer(

    )
    normal = fields.Boolean(

    )

    @api.depends('hours')
    def _mitad(self):
        for record in self:
            if record.day == 5:
                record.mitad = record.hours_sat/2
            else:
                record.mitad = record.hours / 2

    @api.depends('work_hours')
    def _hours_extra(self):
        for record in self:
            if record.day != 5 and record.work_hours > record.hours:
                record.hours_extra = (record.work_hours - record.hours)//1

            elif record.day == 5 and record.normal == True and record.work_hours >= record.hours_sat:
                record.hours_extra = (record.work_hours - record.hours_sat)//1

            elif record.day == 5 and record.normal == False:
                record.hours_extra = record.work_hours

            elif record.work_hours < record.mitad:
                record.hours_extra = False

            elif record.work_hours > record.mitad:
                record.hours_extra = (record.work_hours - record.mitad)//1

    @api.depends('hours_extra', 'cost_extra')
    def _total_extra(self):
        for record in self:
            record.total_extra = record.hours_extra * record.cost_extra

