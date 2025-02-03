# -*- coding: utf-8 -*-

import operator
import logging
from odoo import models, fields, api, exceptions
from datetime import timedelta

_logger = logging.getLogger('move_attendance')

class move_attendance_wizard(models.TransientModel):
    _name = "move.draft.attendance.wizard"
    _description = 'Move Draft Attendance Wizard'
    
    date1 = fields.Datetime('From', required=True)
    date2 = fields.Datetime('To', required=True)
    employee_ids = fields.Many2many('hr.employee', 'move_att_employee_rel', 'employee_id', 'wiz_id')
    
    def move_confirm(self):
        try:
            hr_attendance = self.env['hr.attendance']
            employees = self.employee_ids or self.env['hr.employee'].search([])

            for employee in employees:
                attendances = self.env['zk.report.daily.attendance'].search([
                    ('name', '=', employee.id),
                    ('punching_day', '>=', self.date1),
                    ('punching_day', '<=', self.date2)],
                    order='punching_time asc'
                )

                for att in attendances:
                    if att.punch_type in ['0', '3', '4']:  # Check In, Break In, Overtime In
                        vals = {
                            'employee_id': employee.id,
                            'check_in': att.punching_time,
                            'att_date': att.punching_day,
                            'address_id': att.address_id.id,
                        }
                        created_rec = hr_attendance.create(vals)
                        att.write({'moved': True, 'moved_to': created_rec.id})

                    elif att.punch_type in ['1', '2', '5']:  # Check Out, Break Out, Overtime Out
                        check_out = att.punching_time
                        check_out_date = fields.Date.to_date(check_out)
                        existing_attendance = hr_attendance.search([
                            ('employee_id', '=', employee.id),
                            ('check_in', '<=', check_out),
                            ('check_out', '=', False),
                            ('att_date', '=', check_out_date),
                        ])

                        if existing_attendance:
                            existing_attendance[-1].write({'check_out': check_out})
                            att.write({'moved': True, 'moved_to': existing_attendance[-1].id})
                        else:
                            check_in_time = check_out - timedelta(hours=4)
                            vals = {
                                'employee_id': employee.id,
                                'check_in': check_in_time,
                                'check_out': check_out,
                                'att_date': att.punching_day,
                                'address_id': att.address_id.id,
                            }
                            created_rec = hr_attendance.create(vals)
                            att.write({'moved': True, 'moved_to': created_rec.id})

        except Exception as e:
            raise exceptions.UserError(f"The following error occurred while moving attendances.\n\n{str(e)}")