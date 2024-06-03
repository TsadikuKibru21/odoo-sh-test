from odoo import models, fields

class HREmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    pin = fields.Char(string="PIN", groups="hr.group_hr_user", copy=False,
                      help="PIN used to Check In/Out in the Kiosk Mode of the Attendance application (if enabled in Configuration) and to change the cashier in the Point of Sale application.", required=True)
