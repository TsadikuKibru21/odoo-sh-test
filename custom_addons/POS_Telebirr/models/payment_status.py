from odoo import models, fields

import logging


class PaymentStatus(models.Model):
    # _name = 'telebirr_payment_status'
    _name = 'telebirr.payment.status'

    price = fields.Float(string='Price')
    trace_number = fields.Char(string='Trace Number')
    phone = fields.Char(string='phone')
    status = fields.Char(string='status')
    def find_pay_confirmed_telebirr(self,trace_number):
        logging.info("Phoneeeeee")

        logging.info(trace_number)

        payment_status = self.env['telebirr.payment.status'].sudo().search([('trace_number', '=', trace_number)])
        logging.info(payment_status.status)
        if payment_status.status=="Confirmed":
            logging.info("OOOOOOOOOOOOOOOO")

            return  {
                        'msg': 'Success'
                        }
        # elif payment_status.status=="Failed":
        #     logging.info("FAILEDDDDDDDDDDDDDDDDDDD")

        #     return   {
        #                 'msg': 'Failed'
        #                 }
        # else:
        #     return {
        #                 'msg': 'None'
        #                 }




