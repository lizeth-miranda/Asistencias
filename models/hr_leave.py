# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models, _
#from odoo.exceptions import ValidationError


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
    num_emp = fields.Char(string="Numero Empleado",
                          related="employee_id.codigo",)

    codigo_falta = fields.Char(
        related="holiday_status_id.code", string="Código Falta", store=True)

    type_inci = fields.Selection(
        related="holiday_status_id.tipo_inci", string="Tipo Incidencia",)

    leavee = fields.Boolean(
        string="Falta", compute="compute_leave", readonly=True, store=True,)
    asist = fields.Boolean(string="asistencia",
                           compute="compute_asis", readonly=True, store=True,)
    residente = fields.Many2one('res.users', string='Residente',
                                required=False, readonly=True, default=lambda self: self.env.user.id)

    semana_nom = fields.Char("Semana",
                             compute="compute_semana", store=True,)

    # metodo que obtiene el numero de semana

    @api.depends('request_date_from')
    def compute_semana(self):
        for record in self:
            cadena = self.env['semanas.nomina'].search([
                ('rango1', '<=', record.request_date_from),
                ('rango2', '>=', record.request_date_from),
            ]).mapped('nombre_semana')

            record.semana_nom = ''.join(map(str, (cadena)))

    @api.depends('holiday_status_id')
    def compute_leave(self):

        if self.type_inci in ['falta', 'FALTA']:
            self.leavee = True
            self.asist = False
        else:
            self.leavee = False

    @api.depends('holiday_status_id')
    def compute_asis(self):

        if self.type_inci in ['asis', 'ASISTENCIA']:
            self.asist = True
            self.leavee = False
        else:
            self.asist = False

    # @api.onchange('holiday_status_id')
    # def asis(self):

    #     if self.codigo_falta != 'F' or self.codigo_falta != 'PSG' or self.codigo_falta != 'I' or self.codigo_falta != 'B':
    #         self.asist = True
    #         self.leavee = False
    #     else:
    #         self.asist = False

    def action_approve(self):
        # def enviar_falta(self):
        res = super(hr_lea, self).action_approve()
        # for record in self:
        #     registros_faltas = self.env['nomina.line'].search_count([
        #         ('employee_id', '=', record.employee_id.id,),
        #         ('codigo_empleado', '=', record.num_emp),
        #         ('project', '=', record.account_ids.id),
        #         ('department', '=', record.pues_tra),
        #         ('fecha_inci', '=', record.request_date_from),

        #     ])
        #     if registros_faltas > 0:
        #         raise ValidationError(
        #             _("Uno o varios de los registros ya existen"))

        #     elif not registros_faltas:
        self.env['nomina.line'].create({
            'employee_id': self.employee_id.id,
            'codigo_empleado': self.num_emp,
            'project': self.account_ids.id,
            'department': self.pues_tra,
            'fechaA': self.request_date_from,
            'fecha_inci': self.request_date_from,
            'inci': self.holiday_status_id.name,
            'leavee': self.leavee,
            'asis': self.asist,
            'cost_day': self.cost_day,
            'extra_cost': self.costo_extra,
            'us_id': self.residente.name,
            'semana': self.semana_nom,
            # 'total_inci': self.cost_default,
        })
        # return {
        #     'effect': {
        #         'fadeout': 'slow',
        #         'message': 'Registro Exitoso',
        #         'type': 'rainbow_man',
        #     }
        # }
        return res
