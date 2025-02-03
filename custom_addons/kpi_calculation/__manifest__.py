# kpi_calculation/__manifest__.py
{
    'name': 'KPI Calculation System',
    'version': '17.0',
    'summary': 'System for managing employee KPIs and performance scoring',
    'category': 'Human Resources',
    'author': 'Tsadiku k',
    'website': 'https://odooethiopia.com', 
    'maintainer': 'tsadikuk@gmail.com',
    
    'depends': ['hr', 'hr_attendance','hr_appraisal'],
    'data': [
        'security/ir.model.access.csv',
        'views/kpi_per_position_views.xml',
        'views/hr_appraisal.xml',
        'data/appraisal_criteria_demo.xml',
        'data/ir_cron_data.xml',

    ],
    'installable': True,
    'application': True,
}
