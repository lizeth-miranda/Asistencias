# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models


class hr_lea(models.Model):
    _inherit = 'hr.leave'

    account_ids = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Obra",
    )
    cost_day = fields.Monetary(
        related='employee_id.cost_day',
        string="Cost day",
    )
    costo_extra = fields.Monetary(
        related='employee_id.cost_extra', string="Costo extra",)

    currency_id = fields.Many2one(
        related='employee_id.currency_id',
    )
    pues_tra = fields.Char(
        related="employee_id.department_id.name",
        string="Puesto de Trabajo",
    )
    num_emp = fields.Char(string="Numero Empleado", related="employee_id.codigo",)

    codigo_falta = fields.Char(
        related="holiday_status_id.code", string="Código Falta",)

    leavee = fields.Boolean(
        string="Falta",
    )
    asist = fields.Boolean(string="asistencia",)

    @api.onchange('holiday_status_id')
    def falta(self):

        if self.codigo_falta == 'F' or self.codigo_falta == 'PSG' or self.codigo_falta == 'I' or self.codigo_falta == 'B':
            self.leavee = True
            self.asist = False
        else:
            self.leavee = False

    @api.onchange('holiday_status_id')
    def asis(self):

        if self.codigo_falta != 'F' or self.codigo_falta != 'PSG' or self.codigo_falta != 'I' or self.codigo_falta != 'B':
            self.asist = True
            self.leavee = False
        else:
            self.asist = False

    # def action_approve(self):
    def enviar_falta(self):
        #res = super(hr_lea, self).action_approve()
        for record in self:
            registros_faltas = self.env['nomina.line'].search_count([
                ('employee_id', '=', record.employee_id.id,),
                ('codigo_empleado', '=', record.num_emp),
                ('project', '=', record.account_ids.id),
                ('department', '=', record.pues_tra),
                ('fecha_inci', '=', record.request_date_from),

            ])
            if registros_faltas > 0:
                raise ValidationError(
                    _("Uno o varios de los registros ya existen"))

            elif not registros_faltas:
                self.env['nomina.line'].create({
                    'employee_id': self.employee_id.id,
                    'codigo_empleado': self.num_emp,
                    'project': self.account_ids.id,
                    'department': self.pues_tra,
                    'fecha_inci': self.request_date_from,
                    'inci': self.holiday_status_id.name,
                    'leavee': self.leavee,
                    'asis': self.asist,
                    'cost_day': self.cost_day,
                    'extra_cost': self.costo_extra,
                    # 'total_inci': self.cost_default,
                })
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Registro Exitoso',
                        'type': 'rainbow_man',
                    }
                }
        # return res
