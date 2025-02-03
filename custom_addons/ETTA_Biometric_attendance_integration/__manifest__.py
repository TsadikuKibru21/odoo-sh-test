
{
    'name': 'ETTA Biometric Device',
    'version': '17.0',
    'summary': """Integrating Biometric Device With HR Attendance (Face + Thumb)""",
    'description': 'This module integrates Odoo with the biometric device. (Check below or README.md for compatible devices.)',
    'category': 'Generic Modules/Human Resources',
    'author': 'Tsadiku',
    'company': 'ETTA',
    'website': "www.ethiopiataxi.com",
    'depends': ['base_setup', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/zk_machine_view.xml',
        'views/zk_machine_attendance_view.xml',
        # 'data/download_data.xml',
        # 'views/css.xml'
        # 'wizard/move_attendance_wizard_view.xml',

    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
