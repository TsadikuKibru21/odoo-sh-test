from datetime import timedelta
import logging
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    device_id = fields.Char(string='Biometric Device ID')  

    @api.constrains('device_id')
    def check_unique_deviceid(self):
        records = self.env['hr.employee'].search([('device_id', '=', self.device_id),('device_id', '!=', False ),('id', '!=', self.id)])
        if records:
            raise UserError(_('Another User with same Biometric Device ID already exists.'))

class HrAttendance(models.Model):
    _inherit="hr.attendance"
    address_id = fields.Many2one('res.partner', string='Working Address')
    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        for attendance in self:
            if not attendance.check_out:
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ], limit=1, order="check_in ASC")
class ZkMachine(models.Model):
    _name = 'zk.machine.attendance'
    _inherit = 'hr.attendance'
    _description = "machine attendance"

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """overriding the __check_validity function for employee attendance."""
        pass

    device_id = fields.Char(string='Biometric Device ID')
    punch_type = fields.Selection([('0', 'Check In'),
                                   ('1', 'Check Out'),
                                   ('2', 'Break Out'),
                                   ('3', 'Break In'),
                                   ('4', 'Overtime In'),
                                   ('5', 'Overtime Out')],
                                  string='Punching Type')

    attendance_type = fields.Selection([('1', 'Finger'),
                                        ('15', 'Face'),
                                        ('2','Type_2'),
                                        ('3','Password'),
                                        ('4','Card')], string='Category')
    punching_time = fields.Datetime(string='Punching Time')
    address_id = fields.Many2one('res.partner', string='Working Address')


class ReportZkDevice(models.Model):
    _name = 'zk.report.daily.attendance'
    _order = 'punching_day desc'
    _description = "zk daily report"

    name = fields.Many2one('hr.employee', string='Employee')
    punching_day = fields.Date(string='Date')
    address_id = fields.Many2one('res.partner', string='Working Address')
    attendance_type = fields.Selection([('1', 'Finger'),
                                        ('15', 'Face'),
                                        ('2','Type_2'),
                                        ('3','Password'),
                                        ('4','Card')],
                                       string='Category')
    punch_type = fields.Selection([('0', 'Check In'),
                                   ('1', 'Check Out'),
                                   ('2', 'Break Out'),
                                   ('3', 'Break In'),
                                   ('4', 'Overtime In'),
                                   ('5', 'Overtime Out')], string='Punching Type')
    punching_time = fields.Datetime(string='Punching Time')
    moved = fields.Boolean(string='Moved', default=False)
    
    def action_move(self):
        hr_attendance = self.env['hr.attendance']

        # Process the selected records by employee and in chronological order by punching time
        employees = self.mapped('name')  # Get a unique list of employees
        for employee in employees:
            # Get the records for the current employee, ordered by punching time
            employee_records = self.filtered(lambda r: r.name == employee and not r.moved).sorted(key=lambda r: r.punching_time)
            
            for record in employee_records:
                logging.info(f"Processing record: {record.id}, employee: {record.name.id}")

                # Check if there is an existing open check-in (with no check_out) for this employee
                existing_open_attendance = hr_attendance.search([
                    ('employee_id', '=', employee.id),
                    ('check_out', '=', False),
                ], limit=1, order='check_in desc')

                if existing_open_attendance:
                    # If there is an open check-in, this record will close it (act as a check-out)
                    logging.info(f"Updating Check-Out for existing attendance: {existing_open_attendance.id}")
                    existing_open_attendance.write({'check_out': record.punching_time})
                else:
                    # If there is no open check-in, this record will create a new check-in
                    logging.info(f"Creating new Check-In for employee: {record.name.id}")
                    vals = {
                        'employee_id': employee.id,
                        'check_in': record.punching_time,
                        'address_id': record.address_id.id,
                    }
                    hr_attendance.create(vals)
                
                # Mark the current record as moved
                record.write({'moved': True})

    # def action_move(self):
    #     hr_attendance = self.env['hr.attendance']

    #     selected_records = self

    #     # First move the check-in records
    #     check_in_types = ['0', '3', '4']
    #     check_in_records = selected_records.filtered(lambda r: r.punch_type in check_in_types and not r.moved)
    #     for record in check_in_records.sorted(key=lambda r: r.punching_time):
    #         logging.info(f"Processing Check-In record: {record.id}, punch_type: {record.punch_type}")

    #         existing_attendance = hr_attendance.search([
    #             ('employee_id', '=', record.name.id),
    #             ('check_in', '=', record.punching_time),
    #             ('address_id', '=', record.address_id.id),
    #         ])
    #         logging.info(f"Check In search result: {existing_attendance}")

    #         if not existing_attendance:
    #             vals = {
    #                 'employee_id': record.name.id,
    #                 'check_in': record.punching_time,
    #                 'address_id': record.address_id.id,
    #             }
    #             hr_attendance.create(vals)
    #         record.write({'moved': True})

    #     # Then move the check-out records
    #     check_out_types = ['1', '2', '5']
    #     check_out_records = selected_records.filtered(lambda r: r.punch_type in check_out_types and not r.moved)
    #     for record in check_out_records.sorted(key=lambda r: r.punching_time, reverse=True):
    #         logging.info(f"Processing Check-Out record: {record.id}, punch_type: {record.punch_type}")

    #         check_out = record.punching_time

    #         existing_attendance = hr_attendance.search([
    #             ('employee_id', '=', record.name.id),
    #             ('check_in', '<=', str(check_out)),
    #             ('check_out', '=', False),
    #             ('address_id', '=', record.address_id.id),
    #         ], limit=1, order='check_in desc')
    #         logging.info(f"Check Out search result: {existing_attendance}")

    #         if existing_attendance:
    #             existing_attendance.write({'check_out': check_out})
    #             record.write({'moved': True})
            # else:
            #     emp_cont = self.env['hr.contract'].search([
            #         ('employee_id', '=', record.name.id),
            #     ], limit=1)
            #     if emp_cont:
            #         hours_per_day = emp_cont.resource_calendar_id.hours_per_day
            #         checkin_rule = self.env['checkin.rule'].search([
            #             ('shift_group', '=', emp_cont.resource_calendar_id.id)
            #         ], limit=1)
            #         if checkin_rule:
            #             tot = len(checkin_rule.check_in_attendance_times) + len(checkin_rule.check_out_attendance_times)
            #             cal = 2 * hours_per_day / tot
            #             check_in_time = check_out - timedelta(hours=cal)
            #             vals = {
            #                 'employee_id': record.name.id,
            #                 'check_in': check_in_time,
            #                 'check_out': check_out,
            #                 'address_id': record.address_id.id,
            #             }
            #             hr_attendance.create(vals)
            #             record.write({'moved': True})
            #             logging.info("Check In and Check Out record created")
            #         else:
            #             raise ValidationError(_("No Checkin Rule found for the shift group."))
            #     else:
            #         raise ValidationError(_("No HR Contract found for the employee."))
        # except Exception as e:
        #     raise ValidationError(_("An error occurred while moving attendances to hr.attendance: %s") % str(e))
                
            # Add your logic here

    # def init(self):
    #     tools.drop_view_if_exists(self._cr, 'zk_report_daily_attendance')
    #     self._cr.execute("""
    #         create or replace view zk_report_daily_attendance as (
    #             select
    #                 min(z.id) as id,
    #                 z.employee_id as name,
    #                 z.write_date as punching_day,
    #                 z.address_id as address_id,
    #                 z.attendance_type as attendance_type,
    #                 z.punching_time as punching_time,
    #                 z.punch_type as punch_type
    #             from zk_machine_attendance z
    #                 join hr_employee e on (z.employee_id=e.id)
    #             GROUP BY
    #                 z.employee_id,
    #                 z.write_date,
    #                 z.address_id,
    #                 z.attendance_type,
    #                 z.punch_type,
    #                 z.punching_time
    #         )
    #     """)


