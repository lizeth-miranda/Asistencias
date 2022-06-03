# -*- coding: utf-8 -*-
{
    'name': 'Costo Empleado',
    'version': '13.3',
    'author': 'Demsa',
    'website': '',
    'depends': [
        'hr',
        'hr_expense',
        'account',
        'account_accountant',
        'hr_attendance',
        'hr_timesheet',
        'hr_holidays',
        'sale_management',
        'purchase',
    ],
    'data': [
        # security
        #'security/groups.xml',
        #'security/groupsDisc.xml',
        #'security/semanas_group.xml',
        #'security/ir.model.access.csv',
        # 'security/nominasecurity.xml',
        # data
        # wizards
        #'wizards/nomina_wizard.xml',

        # reports
        #'reports/nomina_semanal.xml',
        # 'reports/formato_papel.xml',
        # demo
        # views
        'views/hr_attendance.xml',
        'views/hr_employee.xml',
       # 'views/hr_leave.xml',
       # 'views/hr_leave_type.xml',
       # 'views/account_analytic.xml',
        'views/account_analytic_account.xml',
        'views/res_user.xml',
        #'views/nomina.xml',
        #'views/server_action_prenomina.xml',
        #'views/dicounts_employee.xml',
        #'views/discounts_loans.xml',
        #'views/purchase_requisition.xml',
        'views/group_acuerdoCompra.xml',
        #'views/group_asistecias_planta.xml',
        #'views/view_asistencias.xml',
        #'views/group_registrarPrenomina.xml',
        'views/group_control_obra.xml',
        'views/group_empleado_usuario.xml',
        #'views/semanas.xml',
        # 'views/account_move.xml',



    ],
}
