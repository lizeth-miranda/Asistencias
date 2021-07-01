# -*- coding: utf-8 -*-
# instruccion para hacer importaciones desde odoo
from odoo import api, fields, models, exceptions, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError


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
    fechaA = fields.Date(string="Fecha Asistencia",
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
        related="employee_id.salary",
        string="Sueldo Semanal",
        readonly=True,
    )
    cost_day = fields.Monetary(
        help="sueldo semanal/6",
        related="employee_id.cost_day",
        string="Costo/Día",
        readonly=True,
    )
    cost_hour = fields.Monetary(
        help="Costo por día/8",
        related="employee_id.timesheet_cost",
        string="Costo/Hora",
        readonly=True,
    )
    extra_cost = fields.Monetary(
        help="sueldo semanal/6/8*2",
        related="employee_id.cost_extra",
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
    account = fields.Char(related="employee_id.cuenta",
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
        related="employee_id.bono",
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
        store=True
    )
    sum_perc_notCarga = fields.Monetary(
        compute="compute_sum_perc_noCS", string="Suma Percepciones", store=True)

    semana_fondo = fields.Monetary(string="Semana de Fondo",)

    pres_personal = fields.Monetary(
        string="Préstamo Personal",)

    # Deducciones
    cre_info = fields.Monetary(
        related="employee_id.credito_info",
        string="Crédito Infonavit"
    )
    # pres_per = fields.Monetary(
    #     string="Préstamo Personal",
    # )
    abono = fields.Monetary(string="Préstamo Personal",
                            related="employee_id.abono")
    des_epp = fields.Monetary(
        string="Desc. EPP Herramienta", related="employee_id.pago")
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
        compute='compute_sumHE', string="total Horas Extras", store=True)

    # calcular costo/dia en una falta
    costo_falta = fields.Monetary(compute="compute_costo_falta", store=True,)

    # suma_costoMO = fields.Monetary(
    #     compute="compute_sumaMO", string="Costo MO Semanal", store=True,)

    nomina = fields.Boolean(default=True, string="nomina",)
    asis = fields.Boolean(string="Asistencia",)

    # Prestamos personales
    datee = fields.Datetime(
        string="Fecha", default=fields.Datetime.now, readonly=False,)
    datee2 = fields.Date(compute="compute_datee")
    total_prestamo = fields.Monetary(
        string="Préstamo", related="employee_id.total_prestamo",)
    abono = fields.Monetary(string="Abono", related="employee_id.abono")
    num_pago = fields.Integer(string="# Pago", compute="compute_num_pago")
    semanas = fields.Float(string="Semanas", related="employee_id.semanas",)
    fecha_pp2 = fields.Date(related="employee_id.onlyfecha_pp",)
    fecha_up2 = fields.Datetime(related="employee_id.fecha_up", string="Fecha última de pago")
    saldo = fields.Monetary(string="Saldo",)
    resta2 = fields.Float()

    # calcular solo fecha de el primer pago
    @ api.depends('datee')
    def compute_datee(self):
        for record in self:
            f1 = record.datee
            date = fields.Datetime.to_string(fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(f1)))[:10]
            record.datee2 = date

    @api.onchange('datee')
    def compute_num_pago(self):

        for rec in self:
            if not rec.fecha_up2:
                rec.num_pago = 0
            else:
                r1 = (rec.fecha_up2 - rec.datee).days
                r2 = r1 / 7
                rec.resta2 = rec.semanas - r2
                rec.num_pago = rec.resta2

                rec.saldo = rec.total_prestamo - \
                    (rec.abono * rec.num_pago)

    # descuentos herramienta
    fecha_desc = fields.Datetime(
        string="Fecha.", default=fields.Datetime.now, readonly=False,)
    fecha_desc2 = fields.Date(compute="compute_fecha_desc2")
    descuento = fields.Monetary(
        string="Total material a cobro", related="employee_id.descuento",)
    rang = fields.Float(string="#Semanas ", related="employee_id.rango",)
    pag = fields.Monetary(string="Cantidad Abonar", related="employee_id.pago")
    fecha_pd2 = fields.Date(related="employee_id.onlyfecha_pd",)
    fecha_fin = fields.Datetime(related="employee_id.fecha_final", string="Fecha Final Pago")
    desc = fields.Text(related="employee_id.desc", string="Descripción",)
    numero_pago = fields.Integer(
        string="#Pago.", compute="compute_numero_pago")
    sal = fields.Monetary(string="Saldo.",)
    resta = fields.Float()

    @ api.depends('fecha_desc')
    def compute_fecha_desc2(self):
        for record in self:
            f2 = record.fecha_desc
            date2 = fields.Datetime.to_string(fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(f2)))[:10]
            record.fecha_desc2 = date2

    @api.onchange('fecha_desc')
    def compute_numero_pago(self):

        for rec in self:
            l1 = (rec.fecha_fin - rec.fecha_desc).days
            l2 = l1 / 7
            rec.resta = rec.rang - l2
            rec.numero_pago = rec.resta

            rec.sal = rec.descuento - (rec.pag * rec.numero_pago)

    @api.depends('start_date', 'end_date')
    def compute_sumHE(self):
        for record in self:
            record.sum_horas_extras = sum(self.env['nomina.line'].search([
                ('fechaA', '>=', record.start_date),
                ('fechaA', '<=', record.end_date),
                ('employee_id', '=', record.employee_id.id),
                # ('reg_sem', 'in', ['week', 'semanal'])
            ]).mapped('hours_extra'))

    # @api.depends('start_date', 'end_date')
    # def compute_sumaMO(self):
    #     for record in self:
    #         record.suma_costoMO = sum(self.env['nomina.line'].search([
    #             ('fechaA', '>=', record.start_date),
    #             ('fechaA', '<=', record.end_date),
    #             #('employee_id', '=', record.employee_id.id),
    #             ('project', '=', record.project.id),
    #         ]).mapped('suma_percep'))

    @api.depends('start_date', 'end_date')
    def hrs_ex_sem(self):
        for record in self:
            record.horas_extras_sem = sum(self.env['nomina.line'].search([
                ('fechaA', '>=', record.start_date),
                ('fechaA', '<=', record.end_date),
                ('employee_id', '=', record.employee_id.id),
                # ('reg_sem', 'in', ['week', 'semanal'])
            ]).mapped('total_extra'))

    @ api.depends('fechaA')
    def _day(self):
        for record in self:
            record.day = record.fechaA.weekday()

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

     # calculo sueldo a pagar
    # calculo del costo de obra con la carga social

    @api.depends('cost_total', 'viat', 'bono', 'pasa', 'bono_even', 'gasolina', 'vacaciones', 'aguin')
    def sum_perc(self):
        for record in self:
            if record.inci != False:
                record.suma_percep = (record.cost_total + record.viat + record.pasa + record.bono +
                                      record.bono_even + record.gasolina +
                                      record.vacaciones + record.prima_vaca + record.aguin) * -1
            else:
                record.suma_percep = (record.cost_total + record.viat + record.pasa + record.bono +
                                      record.bono_even + record.gasolina +
                                      record.vacaciones + record.prima_vaca + record.aguin + record.costo_daycs) * -1
    # calcular las faltas y asistencias
    cant_ausen = fields.Float(
        compute="compute_cant_ausen", string="Cantidad de Ausencias",)
    cant_asis = fields.Float(compute="compute_cant_asis",
                             string="Cantidad de Asistencias",)

    @api.depends('start_date', 'end_date')
    def compute_cant_ausen(self):
        for record in self:
            record.cant_ausen = self.env['nomina.line'].search_count([
                ('fechaA', '>=', record.start_date),
                ('fechaA', '<=', record.end_date),
                ('employee_id', '=', record.employee_id.id),
                ('leavee', '=', True),
                # ('reg_sem', 'in', ['week', 'semanal'])
            ])

    @api.depends('start_date', 'end_date')
    def compute_cant_asis(self):
        for record in self:
            record.cant_asis = self.env['nomina.line'].search_count([
                ('fechaA', '>=', record.start_date),
                ('fechaA', '<=', record.end_date),
                ('employee_id', '=', record.employee_id.id),
                ('asis', '=', True),
                # ('reg_sem', 'in', ['week', 'semanal'])
            ])
    suel_Sem_faltas = fields.Monetary(
        compute="compute_suel_sem_faltas", string="Sueldo semanal con faltas",)

    @api.depends('cost_day', 'cant_asis', 'cant_ausen')
    def compute_suel_sem_faltas(self):
        for rec in self:
            r1 = rec.extra_cost * rec.cant_ausen
            rec.suel_Sem_faltas = (
                rec.cost_day * rec.cant_asis + rec.cost_day) - r1

    # calcular sueldo con nuevo ingreso
    suel_nuevo_ingreso = fields.Monetary(
        compute="compute_suel_nuevo_ingreso", string="Sueldo Nuevo Ingreso",)

    @api.depends('cost_day', 'cant_asis')
    def compute_suel_nuevo_ingreso(self):
        for rec in self:
            rec.suel_nuevo_ingreso = rec.cost_day * rec.cant_asis

    # calculo costo de percepciones sin carga social para la nómina

    @api.depends('reg_sem', 'suel_nuevo_ingreso', 'suel_Sem_faltas', 'sueldo_semanal', 'viat', 'bono', 'pasa', 'bono_even', 'gasolina', 'vacaciones', 'aguin')
    def compute_sum_perc_noCS(self):
        for record in self:
            if record.reg_sem in ['week', 'semanal'] and record.cant_asis == 5:
                record.sum_perc_notCarga = (record.sueldo_semanal + record.viat + record.pasa + record.bono +
                                            record.bono_even + record.gasolina +
                                            record.vacaciones + record.prima_vaca + record.aguin + record.semana_fondo + record.pres_personal)

            elif record.reg_sem in ['week', 'semanal'] and record.cant_ausen > 0:
                record.sum_perc_notCarga = (record.suel_Sem_faltas + record.viat + record.pasa + record.bono +
                                            record.bono_even + record.gasolina +
                                            record.vacaciones + record.prima_vaca + record.aguin + record.semana_fondo + record.pres_personal)

            elif record.reg_sem in ['week', 'semanal'] and record.cant_asis < 5 and record.cant_ausen == 0:
                record.sum_perc_notCarga = (record.suel_nuevo_ingreso + record.viat + record.pasa + record.bono +
                                            record.bono_even + record.gasolina +
                                            record.vacaciones + record.prima_vaca + record.aguin + record.semana_fondo + record.pres_personal)

    @api.depends('reg_sem', 'cre_info', 'fona', 'abono', 'otros_desc')
    def sum_dedu(self):
        for record in self:
            if record.reg_sem in ['week', 'semanal'] and record.saldo != 0 and record.datee2 >= record.fecha_pp2 and record.fecha_desc2 >= record.fecha_pd2:
                record.suma_dedu = record.cre_info + record.fona + \
                    record.abono + record.des_epp + record.otros_desc

            elif record.reg_sem in ['week', 'semanal'] and record.saldo != 0 and record.datee2 < record.fecha_pp2 and record.fecha_desc2 < record.fecha_pd2:
                record.suma_dedu = record.cre_info + record.fona + record.otros_desc

            elif record.reg_sem in ['week', 'semanal'] and record.saldo == 0:
                record.suma_dedu = record.cre_info + \
                    record.fona + record.otros_desc

    @ api.depends('reg_sem', 'start_date', 'end_date')
    def suel_pagar(self):
        for record in self:
            if record.reg_sem in ['week', 'semanal']:
                record.sueldo_pagar = (
                    record.sum_perc_notCarga + record.horas_extras_sem) - record.suma_dedu

    # create a new line, as none existed before

    @ api.constrains('date', 'name', 'amount')
    def acco_line(self):
        for record in self:
            record.state = 'confirm'
            account_line = self.env['account.analytic.line'].search_count([
                ('date', '=', record.fechaA),
                ('name', '=', record.employee_id.name),
                ('job_pos', '=', record.department),
                ('account_id', '=', record.project.id),
                ('amount', '=', record.suma_percep),
            ])
            if account_line > 0:
                raise ValidationError(
                    _("Uno o varios de los registros ya fueron Confirmados"))

            elif not account_line:
                self.env['account.analytic.line'].create({
                    'date': record.fechaA,
                    'name': record.employee_id.name,
                    'nom': record.nomina,
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
    
    @ api.depends('empĺoyee_id')
    def cron_check_employees(self):

        for record in self:
            employeecount = record.env['nomina.line'].search([
                # ('employee_id', '=', record.employee_id.id),
                ('fechaA', '>=', record.start_date),
                ('fechaA', '<=', record.end_date),
                ('reg_sem', 'in', ['week', 'semanal']),
                #('state', 'in', ['draft', 'Borrador']),

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
   
