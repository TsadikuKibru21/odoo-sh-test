import pytz
import sys
from datetime import datetime,date
from datetime import timedelta
from . import base
import logging
import binascii
import os
import platform
import subprocess
import time
from dateutil.relativedelta import relativedelta
import math


from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)
# try:
#     from . base import ZK,const
# except ImportError:
#     _logger.error("Unable to import pyzk library. Try 'pip3 install pyzk'.")

class HrAttendance(models.Model):
    _inherit = 'hr.employee'

    user_device_id = fields.Char(string='User Biometric Device ID')
    machine_id=fields.Many2one('zk.machine',string='Biometric Machine')
        # @api.model
    # def cron_set_attedance_checkout(self):
    #     attendance_object=self.env['hr.attendance']
    #     records = attendance_object.search([('check_out', '=', False), ('check_in', '!=', False)]):
    #     for record in records:
    #         record.check_out = record.check_in


class ZkMachine(models.Model):
    _name = 'zk.machine'
    _description = "Zk machine model"
    
    name = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port No', required=True, default="4370")
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    zk_timeout = fields.Integer(string='ZK Timeout', required=True, default="120")
    zk_after_date =  fields.Datetime(string='Attend Start Date', help='If provided, Attendance module will ignore records before this date.')
    lipping = fields.Datetime(string="Last Check In")
    

    
    # def device_connect(self, zkobj):
    #     try:
    #         conn =  zkobj.connect()
    #         return conn
    #     except:
    #         _logger.info("zk.exception.ZKNetworkError: can't reach device.")
    #         raise UserError("Connection To Device cannot be established.")
    #         return False

    
    # def device_connect(self, zkobj):
    #     for i in range(10):
    #         try:
    #             conn =  zkobj.connect()
    #             return conn
    #         except:
    #             _logger.info("zk.exception.ZKNetworkError: can't reach device.")
    #             conn = False
    #     return False
    # def disable_machine_connection(self):
    #     machine_ip=self.name
    #     zk_port= self.port_no
    #     timeout=self.zk_timeout
    #     try:
    #         zk=ZK(machine_ip,port=zk_port,timeout=timeout,password=0,force_udp=False,ommit_ping=False)
    #     except NameError:
    #         raise UserError("Try Again")
    #     con=self.device_connect(zk)
    #     if con:
    #         con.disable_device()
    #     else:
    #         raise UserError("Can't disable device")
    # def enable_machine_connection(self):
    #     machine_ip=self.name
    #     zk_port= self.port_no
    #     timeout=self.zk_timeout
    #     try:
    #         zk=ZK(machine_ip,port=zk_port,timeout=timeout,password=0,force_udp=False,ommit_ping=False)
    #     except NameError:
    #         raise UserError("Try Again")
    #     con=self.device_connect(zk)
    #     if con:
    #         con.enable_device()
    #     else: 
    #         raise UserError("Can't Enable Device")

    # def lock_machine_connection(self):
    #     machine_ip=self.name
    #     zk_port= self.port_no
    #     timeout=self.zk_timeout
    #     try:
    #         zk=ZK(machine_ip,port=zk_port,timeout=timeout,password=0,force_udp=False,ommit_ping=False)
    #     except NameError:
    #         raise UserError("Try Again")
    #     con=self.device_connect(zk)
    #     if con:
    #         con.get_lock_state()
    #     else:
    #         raise UserError("Can't disable device")

    # def unlock_machine_connection(self):
    #     machine_ip=self.name
    #     zk_port= self.port_no
    #     timeout=self.zk_timeout
    #     try:
    #         zk=ZK(machine_ip,port=zk_port,timeout=timeout,password=0,force_udp=False,ommit_ping=False)
    #     except NameError:
    #         raise UserError("Try Again")
    #     con=self.device_connect(zk)
    #     if con:
    #         con.unlock()
    #     else:
    #         raise UserError("Can't disable device")


    
    # def try_connection(self):
    #     for r in self:
    #         machine_ip = r.name
    #         if platform.system() == 'Linux':
    #             response = os.system("ping -c 1 " + machine_ip)
    #             if response == 0:
    #                 raise UserError("Biometric Device is Up/Reachable.")
    #             else:
    #                 raise UserError("Biometric Device is Down/Unreachable.") 
    #         else:
    #             prog = subprocess.run(["ping", machine_ip], stdout=subprocess.PIPE)
    #             if 'unreachable' in str(prog):
    #                 raise UserError("Biometric Device is Down/Unreachable.")
    #             else:
    #                 raise UserError("Biometric Device is Up/Reachable.")  
    
    
    # def clear_attendance(self):
    #     for info in self:
    #         try:
    #             machine_ip = info.name
    #             zk_port = info.port_no
    #             timeout = info.zk_timeout
    #             try:
    #                 zk = ZK(machine_ip, port = zk_port , timeout=timeout, password=0, force_udp=False, ommit_ping=False)
    #             except NameError:
    #                 raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))                
    #             conn = self.device_connect(zk)
    #             if conn:
    #                 conn.enable_device()
    #                 clear_data = zk.get_attendance()
    #                 if clear_data:
    #                     #conn.clear_attendance()
    #                     self._cr.execute("""delete from zk_machine_attendance""")
    #                     conn.disconnect()
    #                     raise UserError(_('Attendance Records Deleted.'))
    #                 else:
    #                     raise UserError(_('Unable to clear Attendance log. Are you sure attendance log is not empty.'))
    #             else:
    #                 raise UserError(_('Unable to connect to Attendance Device. Please use Test Connection button to verify.'))
    #         except:
    #             raise ValidationError('Unable to clear Attendance log. Are you sure attendance device is connected & record is not empty.')

    # def zkgetuser(self, zk):
    #     try:
    #         users = zk.get_users()
    #         print(users)
    #         return users
    #     except:
    #         raise UserError(_('Unable to get Users.'))

    # @api.model
    # def cron_download(self):
    #     machines = self.env['zk.machine'].search([])
    #     for machine in machines :
    #         machine.download_attendance()

    # @api.model
    # def cron_set_attedance_checkout(self):
    #     attendance_object=self.env['hr.attendance']
    #     records = attendance_object.search([('check_out', '=', False), ('check_in', '!=', False)]):
    #     for record in records:
    #         record.check_out = record.check_in
        
    
    # def download_attendance(self):
    #     _logger.info("++++++++++++Cron Executed++++++++++++++++++++++")
    #     zk_attendance = self.env['zk.machine.attendance']
    #     att_obj = self.env['hr.attendance']

    #     for info in self:
    #         machine_ip = info.name
    #         zk_port = info.port_no
    #         timeout = info.zk_timeout
    #         _logger.info("Attempting to connect to the device at IP: {machine_ip}, Port: {zk_port}")
    #         try:
    #             zk = ZK(machine_ip, port = zk_port , timeout=timeout, password=0, force_udp=False, ommit_ping=False)
    #         except NameError:
    #             raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))
    #         conn = self.device_connect(zk)
    #         if conn:
    #             _logger.info("Connection established successfully to device at IP: {machine_ip}, Port: {zk_port}")
    #             # conn.disable_device() #Device Cannot be used during this time.
    #             try:
    #                 user = conn.get_users()
    #                 _logger.info("Users fetched from IP: {machine_ip}, Port: {zk_port}: {users}")
    #             except:
    #                 _logger.info("Failed to fetch users from IP: {machine_ip}, Port: {zk_port}: {e}")
    #                 user = False
    #             try:
    #                 attendance = conn.get_attendance()
    #             except:
    #                 attendance = False
    #             if attendance:
    #                 _logger.info("attendance########################################################################")
    #                 #_logger.info(attendance)
                    
    #                 for each in attendance:
    #                     atten_time = each.timestamp
    #                     atten_time = datetime.strptime(atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    #                     if info.zk_after_date == False:
    #                         tmp_zk_after_date = datetime.strptime('2023-07-01',"%Y-%m-%d")
    #                     else:
    #                         tmp_zk_after_date = datetime.strptime(info.zk_after_date,'%Y-%m-%d %H:%M:%S')
    #                     if atten_time != False and atten_time > tmp_zk_after_date:
    #                         local_tz = pytz.timezone(
    #                             self.env.user.partner_id.tz or 'GMT')
    #                         local_dt = local_tz.localize(atten_time, is_dst=None)
    #                         utc_dt = local_dt.astimezone(pytz.utc)
    #                         utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
    #                         atten_time = datetime.strptime(
    #                             utc_dt, "%Y-%m-%d %H:%M:%S")
    #                         tmp_utc = local_dt.astimezone(pytz.utc)
    #                         tmp_attend = tmp_utc.strftime("%m-%d-%Y %H:%M:%S")
    #                         atten_time = fields.Datetime.to_string(atten_time)
    #                         if user:
    #                             for uid in user:
    #                                 if uid.user_id == each.user_id:
    #                                     get_user_id = self.env['hr.employee'].search(
    #                                         [('device_id', '=', each.user_id)])
    #                                     if get_user_id:
    #                                         duplicate_atten_ids = zk_attendance.search(
    #                                             [('device_id', '=', each.user_id), ('punching_time', '=', atten_time)])
    #                                         if duplicate_atten_ids:
    #                                             continue
    #                                         else:
    #                                             _logger.info("No attendance records found on device at IP: {machine_ip}, Port: {zk_port}.")
    #                                             zk_attendance.create({'employee_id': get_user_id.id,
    #                                                                 'device_id': each.user_id,
    #                                                                 'attendance_type': str(each.status),
    #                                                                 'punch_type': str(each.punch),
    #                                                                 'punching_time': atten_time,
    #                                                                 'address_id': info.address_id.id})


                                                                            

    #                                             att_var = att_obj.search([('employee_id', '=', get_user_id.id),
    #                                                                     ('check_out', '=', False)])
                                                
    #                                             attendance_rec = self.env['hr.attendance'].search([])



    #                                             # att_checkin =att_obj.search([('employee_id','=',get_user_id.id),
    #                                             #                            ([('check_in','=',False)])


    #                                             # att_var_checkin=att_obj.search([('employee_id','=',get_user_id.id)]),
    #                                             #                               ('check_in','=',False)

    #                                             # if each.punch == 0: #check-in
    #                                             #     if not att_var:
    #                                             #         attend_rec_tmp = att_obj.search([('employee_id', '=', get_user_id.id),('check_out', '>', tmp_attend)])
    #                                             #         if not attend_rec_tmp:
    #                                             #             att_obj.create({'employee_id': get_user_id.id,
    #                                             #                             'check_in': atten_time})

    #                                             # if each.punch == 1: #check-out
    #                                             #     if len(att_var) == 1:
    #                                             #         att_var.write({'check_out': atten_time})
    #                                             #     else:
    #                                             #         att_var1 = att_obj.search([('employee_id', '=', get_user_id.id)])
    #                                             #         if att_var1:
    #                                             #             att_var1[-1].write({'check_out': atten_time})

    #                                             att_var2=att_obj.search([('employee_id','=',get_user_id.id),
    #                                                                    ('check_in','=',False)])

    #                                             # last_check_in=att_obj.search([('employee_id','=',get_user_id.id),
    #                                             #                         ('check_in','<=',atten_time)])

    #                                             last_check_out=att_obj.search([('employee_id','=',get_user_id.id),
    #                                                                          ('check_out','<=',atten_time)])

    #                                             # punching_time_diff=atten_time-last_check_in
    #                                             # punching_time_diff_seconds=punching_time_diff.total_seconds()


                                                
    #                                             if not att_var:
    #                                                 # attend_rec_tmp = att_obj.search([('employee_id', '=', get_user_id.id),('check_out', '>', tmp_attend)])

    #                                                 # if not attend_rec_tmp:
    #                                                 att_obj.create({'employee_id':get_user_id.id,
    #                                                                'check_in':atten_time})
    #                                             elif att_var:

    #                                                 # last_check_in=att_obj.search([('employee_id','=',get_user_id.id),
    #                                                                      # ('check_in','<=',atten_time)])

    #                                                 last_check_in=att_obj.search([('employee_id','=',get_user_id.id)])
    #                                                 last_check_out=att_obj.search([('employee_id','=',get_user_id.id)])



    #                                                 # last_punching=last_check_in.check_in
    #                                                 # converted_last_check_in=datetime.datetime.strptime(last_punching.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)



    #                                                 atten_check_in = datetime.strptime(atten_time, "%Y-%m-%d %H:%M:%S")
    #                                                 # converted_atten_check_in=datetime.datetime.strptime(atten_time.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)

    #                                                 # check_out_time-check_in_time
    #                                                 lipping = datetime.now().replace(year=2020).date()
    #                                                 outing = datetime.now().replace(year=2020).date()
    #                                                 hero=timedelta(hours=14,minutes=0)

    #                                                 for xx in last_check_in:
    #                                                     if lipping == datetime.now().replace(year=2020).date():
    #                                                         lipping = xx.check_in
    #                                                     else:
    #                                                         lipper=max(lipping,xx.check_in)
    #                                                         lipping=lipper

    #                                                 lipo=atten_check_in-lipping
    #                                                 if lipo>hero:
    #                                                     att_var.write({'check_out':lipping})
    #                                                     att_obj.create({'employee_id':get_user_id.id,
    #                                                                'check_in':atten_time})
    #                                                 else:
    #                                                     att_var.write({'check_out':atten_time})



    #                                                     # if len(att_var)==1:
    #                                                     #     att_var.write({'check_out':atten_time})
    #                                                     # else:
    #                                                     #     att_var1 = att_obj.search([('employee_id', '=', get_user_id.id)])
    #                                                     #     if att_var1:
    #                                                     #         att_var1[-1].write({'check_out': atten_time})
                                                                

    #                                     else:
    #                                         pass
    #                                 else:
    #                                     pass
    #                 # conn.enable_device() #Enable Device Once Done.
    #                 conn.disconnect
    #                 return True
    #             else:
    #                 raise UserError(_('No attendances found in Attendance Device to Download.'))
    #                 # conn.enable_device() #Enable Device Once Done.
    #         else:
    #             _logger.info("Unable to connect to Attendance Device")
    #             raise UserError(_('Unable to connect to Attendance Device. Please use Test Connection button to verify.'))
