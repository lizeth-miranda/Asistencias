from odoo import api, fields, models


class Worktime(models.Model):
    _inherit = 'resource.calendar.attendance'

    hours = fields.Float(
        compute="_hours",
    )

    def _hours(self):
        for record in self:
            record.hours = record.hour_to - record.hour_from
        return record
