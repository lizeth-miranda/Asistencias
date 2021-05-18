# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta


class Nomina(models.Model):
    _name = "nomina.line"
    _description = 'Registro de Nomina'

    us_id = fields.Char(string="Residente",)
    type_resi = fields.Char(string="Tipo",)
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Trabajador",
        readonly=True,
    )
    department = fields.Char(
        string="Departamento",
        readonly=True,
    )
    empre = fields.Selection(related="employee_id.empresa", string="Empresa")
    project = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Obra",
        readonly=True,
    )
    fecha = fields.Date(string="Fecha Asistencia",
                        required=True, default=fields.Date.today, readonly=True,)

    check_in = fields.Float(string="Entrada",)
    check_out = fields.Float(string="Salida",)

    worked_hours = fields.Float(
        help="Horales laborales + horas extras",
        string="Horas Trabajadas",
        compute='_compute_worked_hours',
        store=True,
    )
    hours_extra = fields.Float(
        help="horas trabajadas - horas laborales",
        string="Horas Extras",
        compute='_hours_extra',
        store=True,
    )
    total_extra = fields.Monetary(
        help="Horas extras * Costo/ hora extra",
        string="Total Extra",
        compute='compute_total_extra',
        store=True,
        readonly=True,
    )
    total_inci = fields.Monetary(string="Total Incidencia")
    cost_total = fields.Monetary(
        help="costo/ día + total extra",
        compute='compute_cost_total',
        store=True,
        readonly=True,
        string="Costo total/Día",
    )
    currency_id = fields.Many2one(
        related='employee_id.currency_id',
    )
    puesto_trabajo = fields.Many2one(
        related="employee_id.department_id",
        string="Puesto",
    )
    codigo_empleado = fields.Char(
        related="employee_id.cod_emp",
        string="# empleado",
    )
    sueldo_semanal = fields.Monetary(
        string="Sueldo Semanal",
        readonly=True,
    )
    cost_day = fields.Monetary(
        help="sueldo semanal/6",
        string="Costo/Día",
        store=True,
        readonly=True,
    )
    cost_hour = fields.Monetary(
        help="Costo por día/8",
        string="Costo/Hora",
        readonly=True,
    )
    extra_cost = fields.Monetary(
        help="sueldo semanal/6/8*2",
        string="Costo Extra/hr",
        readonly=True,
    )
    cost_default = fields.Monetary(
        help="Costo por día + carga social",
        related='employee_id.cost_default',
        string="Costo/Falta",
    )
    hours = fields.Float(
        related="employee_id.horas_lab",
        string="Horas laborales",
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
        string="Horas laborales sábados",
    )
    hrs_lab_in = fields.Float(related="employee_id.horas_lab_in",)
    Date = fields.Date(
        compute='_Date',
        store=True,
    )
    nomina_date = fields.Date(
        default=fields.Date.context_today,
    )
    notas = fields.Text(
        string="Notas",
    )
    # total_hours = fields.Float(
    #     compute='_total_hours',
    #     # store=True,
    # )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
    ], string='Status', readonly=True, default='draft', store=True,)

    responsible_id = fields.Many2one(
        comodel_name='res.users',
        ondelete='set null',
        index=True,
    )
    inci = fields.Char(string="Incidencia",)
    leavee = fields.Boolean(string="Falta",)
    # cuentas bancarias
    account = fields.Char(relate="employee_id.cuenta",
                          string="Cuenta de depósito",)
    cla = fields.Char(related="employee_id.clabe",
                      string="CLABE Interbancaria",)
    bank = fields.Many2one(related="employee_id.banco", string="Banco",)
    # PERCEPCIONES

    viat = fields.Monetary(
        string="Viáticos"
    )
    pasa = fields.Monetary(
        string="Pasaje",
    )
    bono = fields.Monetary(
        string="Bono Fijo",
    )
    bono_even = fields.Monetary(
        string="Bono Eventual",
    )
    gasolina = fields.Monetary(
        string="Gasolina",
    )
    vacaciones = fields.Monetary(
        string="Vacaciones",
    )
    prima_vaca = fields.Monetary(
        string="Prima Vacacional",
    )
    aguin = fields.Monetary(
        string="Aguinaldo",
    )
    costo_daycs = fields.Monetary(
        related="employee_id.costo_dayCS",
    )
    suma_percep = fields.Monetary(
        help="costo/día + total extra + carga social",
        compute="sum_perc",
        string="Costo MO",
        store=True,
    )
    sum_perc_notCarga = fields.Monetary(
        compute="compute_sum_perc_noCS", string="Suma Percepciones", store=True,)
    
    semana_fondo = fields.Monetary(string="Semana de Fondo",)

    # Deducciones
    cre_info = fields.Monetary(
        related="employee_id.credito_info",
        string="Crédito Infonavit"
    )
    pres_per = fields.Monetary(
        string="Préstamo Personal",
    )
    des_epp = fields.Monetary(
        string="Desc. EPP Herramienta",
    )
    otros_desc = fields.Monetary(
        string="Otros Descuentos",
    )
    sueldo_pagar = fields.Monetary(
        help="(Sueldo semanal + Suma percepciones + suma hrs extras) - deducciones ",
        string="Sueldo a pagar",
        compute="suel_pagar",
        store=True,
    )
    fona = fields.Monetary(
        related="employee_id.credito_fona",
        string="Crédito Fonacot",
    )
    suma_dedu = fields.Monetary(
        string="Suma Deducciones",
        compute="sum_dedu",
        store=True
    )
    # Costo semanal
    reg_sem = fields.Selection([('week', 'Semanal')], string='Tipo Registro', )
    start_date = fields.Date(string="Fecha Inicial",
                             )
    end_date = fields.Date(string="Fecha Final",
                           )
    # sueldo_final_sem = fields.Monetary(
    #     compute='sueldo_pagar_sem', string='Sueldo final', store=True,)
    # suel_semanal = fields.Monetary(
    #     compute='sueldo_sem', string='Sueldo Semanal', store=True,)
    horas_extras_sem = fields.Monetary(
        compute='hrs_ex_sem', string='Suma Hrs Extras', store=True,)
    sum_horas_extras = fields.Float(
        compute='compute_sumHE', string="TotalHoras Extras", store=True)

    # calcular costo/dia en una falta
    costo_falta = fields.Monetary(compute="compute_costo_falta", store=True,)

    # @api.depends('start_date', 'end_date')
    # def sueldo_sem(self):
    #     for record in self:
    #         record.suel_semanal = sum(self.env['nomina.line'].search([
    #             ('fecha', '>=', record.start_date),
    #             ('fecha', '<=', record.end_date),
    #             ('employee_id', '=', record.employee_id.id),
    #             # ('reg_sem', 'in', ['week', 'semanal'])
    #         ]).mapped('cost_total'))

    # @api.depends('start_date', 'end_date')
    # def sueldo_pagar_sem(self):
    #     for record in self:
    #         record.sueldo_final_sem = sum(self.env['nomina.line'].search([
    #             ('fecha', '>=', record.start_date),
    #             ('fecha', '<=', record.end_date),
    #             ('employee_id', '=', record.employee_id.id),
    #             # ('reg_sem', 'in', ['week', 'semanal'])
    #         ]).mapped('sueldo_pagar'))
    @api.depends('start_date', 'end_date')
    def compute_sumHE(self):
        for record in self:
            record.sum_horas_extras = sum(self.env['nomina.line'].search([
                ('fecha', '>=', record.start_date),
                ('fecha', '<=', record.end_date),
                ('employee_id', '=', record.employee_id.id),
                # ('reg_sem', 'in', ['week', 'semanal'])
            ]).mapped('hours_extra'))

    @api.depends('start_date', 'end_date')
    def hrs_ex_sem(self):
        for record in self:
            record.horas_extras_sem = sum(self.env['nomina.line'].search([
                ('fecha', '>=', record.start_date),
                ('fecha', '<=', record.end_date),
                ('employee_id', '=', record.employee_id.id),
                # ('reg_sem', 'in', ['week', 'semanal'])
            ]).mapped('total_extra'))

    @ api.depends('fecha')
    def _day(self):
        for record in self:
            record.day = record.fecha.weekday()

    @ api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for rec in self:
            if rec.check_out:
                rec.worked_hours = rec.check_out-rec.check_in
            else:
                rec.worked_hours = False

    @ api.depends('worked_hours')
    def _hours_extra(self):
        for record in self:
            if record.day != 5 and record.worked_hours >= record.hours:
                record.hours_extra = (record.worked_hours-record.hours) // 1

            elif record.day == 5 and record.type_resi == 'planta':
                record.hours_extra = record.worked_hours

            elif record.day == 5 and record.type_resi == 'obra':
                record.hours_extra = record.worked_hours-record.hours_sat

            elif record.day == 6:
                record.hours_extra = record.worked_hours

    @ api.depends('hours_extra')
    def compute_total_extra(self):
        for record in self:
            if record.hours_extra == 0:
                record.total_extra = False
            else:
                record.total_extra = record.hours_extra * record.extra_cost

    @ api.depends('hrs_lab_in', 'hours_extra')
    def compute_cost_total(self):
        for record in self:
            if record.day != 5:
                # t0 = record.worked_hours-record.hours_extra
                t1 = (record.hrs_lab_in * record.cost_hour)
                record.cost_total = (t1 + record.total_extra)

            elif record.day == 5 and record.type_resi == 'obra':
                t1 = (record.hrs_lab_in * record.cost_hour)
                record.cost_total = t1 + record.total_extra

            elif record.day == 5 and record.type_resi == 'planta':
                record.cost_total = record.total_extra

            elif record.day == 6:
                record.cost_total = record.total_extra

    @api.depends('leavee')
    def compute_costo_falta(self):
        for rec in self:
            if rec.leavee == True:
                rec.cost_total = rec.cost_default

        # create a new line, as none existed before

    @ api.constrains('fecha')
    def acco_line(self):
        for record in self:
            record.state = 'confirm'
            account_line = self.env['account.analytic.line'].search_count([
                ('date', '=', record.fecha),
                ('name', '=', record.employee_id.name),
                ('job_pos', '=', record.department),
                ('account_id', '=', record.project.id),
                ('amount', '=', record.suma_percep),
            ])
            if account_line > 0:
                raise ValidationError(_("Los registros ya existen"))

            elif not account_line:
                self.env['account.analytic.line'].create({
                    'date': record.fecha,
                    'name': record.employee_id.name,
                    'job_pos': record.department,
                    'account_id': record.project.id,
                    'amount': record.suma_percep,
                })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Registro Exitoso',
                'type': 'rainbow_man',
            }
        }
    # calculo sueldo a pagar
    # calculo del costo de obra con la carga social

    @api.depends('cost_total', 'viat', 'bono', 'pasa', 'bono_even', 'gasolina', 'vacaciones', 'aguin')
    def sum_perc(self):
        for record in self:
            record.suma_percep = (record.cost_total + record.viat + record.pasa + record.bono +
                                  record.bono_even + record.gasolina +
                                  record.vacaciones + record.prima_vaca + record.aguin + record.costo_daycs) * -1

    # calculo costo de percepciones sin carga social
    @api.depends('cost_total', 'viat', 'bono', 'pasa', 'bono_even', 'gasolina', 'vacaciones', 'aguin')
    def compute_sum_perc_noCS(self):
        for record in self:
            record.sum_perc_notCarga = (record.sueldo_semanal + record.viat + record.pasa + record.bono +
                                        record.bono_even + record.gasolina +
                                        record.vacaciones + record.prima_vaca + record.aguin + record.semana_fondo)

    @api.depends('cre_info', 'fona', 'pres_per', 'otros_desc')
    def sum_dedu(self):
        for record in self:
            record.suma_dedu = record.cre_info + \
                record.pres_per + record.des_epp + record.otros_desc

    @ api.depends('start_date', 'end_date')
    def suel_pagar(self):
        for record in self:

            record.sueldo_pagar = (
                record.sum_perc_notCarga + record.horas_extras_sem) - record.suma_dedu

# if record.reg_sem in ['week', 'semanal']:
    # funcion para revisar que no falten empleados de registrar su nomina en algun dia de la semana o en la semana completa

    @api.depends('empĺoyee_id')
    def cron_check_employees(self):

        for record in self:
            employeecount = record.env['nomina.line'].search([
                #('employee_id', '=', record.employee_id.id),
                # ('fecha', '>=', record.start_date),

                ('reg_sem', 'in', ['week', 'semanal']),
                ('state', 'in', ['draft', 'Borrador']),

            ]).mapped('employee_id.name')
        print(employeecount)

        for record in self:
            employeecount2 = self.env['hr.employee'].search([
                ('empresa', 'in', ['enterprise2', 'DEMSA']), ]).mapped('name')
            print(employeecount2)

        resta = set(employeecount2) - set(employeecount)
        print(resta)

        if resta:
            raise ValidationError(_("Registros de nómina faltantes para: %(resta)s") % {
                'resta': resta,
            })
        else:
            raise ValidationError(_("Todo esta correcto"))

        # for record in self:
        #     employeecount2 = self.env['hr.employee'].search(
        #         [('id', 'not in', record.employee_id.ids),]).mapped('name')
        # print(employeecount2)
        #
        #

            

