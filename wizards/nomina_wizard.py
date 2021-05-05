from odoo import api, fields, models, _


class Nominamywizard(models.TransientModel):
    _name = 'nomina.wizard'
    _description = "Wizard: Obetener un informe de la nómina semanal"

    date_start = fields.Date(string="Fecha Inicial",
                             required=True, default=fields.Date.today)
    date_end = fields.Date(string="Fecha Final",
                           required=True, default=fields.Date.today)

    # @api.multi
    def get_report(self):

        nomina = self.env['nomina.line']
        domain = [
            ('fecha', '>=', self.date_start),
            ('fecha', '<=', self.date_end),
            ('reg_sem', 'in', ['week', 'semanal']),

        ]
        nominaField = [
            'employee_id',
            'department',
            'project',
            'account',
            'cla',
            'bank',
            'suel_semanal',
            'horas_extras_sem',
            'sueldo_final_sem',


        ]
        nominaRecords = nomina.search_read(domain, nominaField)
        data = {
            # ~ 'doc_ids': self.ids,
            # ~ 'doc_model': self.env['covid_19.date.report.wizard'],
            # ~ 'docs': self,
            'nominaRecords': nominaRecords,
            'date_start': self.date_start,
            'date_end': self.date_end,
        }
        return self.env.ref('costoempleado.nomina_semanal_report').with_context(landscape=True).report_action(self, data=data)

    #     data = {
    #         'model': 'nomina.wizard',
    #         'ids': self.ids,
    #         'form': {
    #             'date_start': self.date_start, 'date_end': self.date_end,
    #         },
    #     }

    # ref `module_name.report_id` as reference.
