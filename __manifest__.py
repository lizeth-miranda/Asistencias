# -*- coding: utf-8 -*-
{
    'name': 'Costo Empleado',
    'version': '13.0.0.4.0',
    'author': 'Demsa',
    'website': '',
    'depends': [
        'hr',
        'account',
        'account_accountant',
        'hr_attendance',
        'hr_timesheet',
        'hr_holidays',
    ],
    'data': [
        # security
        # data
        # demo
        # reports
        # views
        'views/hr_attendance.xml',
        'views/hr_employee.xml',
        'views/hr_leave.xml',
        'views/account_analytic.xml',
        'views/account_analytic_account.xml',
        'views/res_user.xml',

    ],
}
