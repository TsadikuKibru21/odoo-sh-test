

from odoo.http import request

from odoo import http, _
import json

import logging


_logger = logging.getLogger(__name__)
import logging

class TeleBirr(http.Controller):
    @http.route('/payment/telebirr',auth='public', type='json', methods=['POST'], csrf=False)
    def tele_callback(self,**k):
 
        jsondata = json.loads(request.httprequest.data)
        logging.info("Traace_nooooo")

        trace_no=jsondata.get('trace_no')
        logging.info(trace_no)

        payment_status = http.request.env['telebirr.payment.status'].sudo().search([('trace_number', '=', trace_no)])
        logging.info("statussssss")

        logging.info(jsondata.get('msg'))
        if jsondata.get('msg')=='Confirmed':
            if payment_status:
                
                logging.info("Confirmedddddd")

                payment_status.write({'status': "Confirmed"})
        elif jsondata.get('msg')=='Failed':
            logging.info("FALED222222222222222")

            payment_status.write({'status': "Failed"})
        else:
            payment_status.write({'status': "None"})







    @http.route('/create_payment', type='json', auth='public', csrf=False)
    def create_resource_endpoint(self, **kw):
        try:
            payment_status = request.env['telebirr.payment.status'].create({
                'price': kw.get("price"),
                'trace_number': kw.get("trace_number"),
                'phone': kw.get("phone"),
            })

            _logger.info("Payment status created successfully: %s", payment_status)

            return True
        except Exception as e:
            _logger.error("Error occurred while creating payment status: %s", e)
            return False














#     # @http.route('/send_request_telebirr', type='json', auth='public', csrf=False)
#     # def send_request_telebirr(self, data):
      
#     #     data['apiKey'] = 'f77cdc52d18111ee9bc8005056a4ed36'
#     #     data['payerId']= '19'
#     #     headers = {'Content-Type': 'application/json'}
#     #     _logger.info("DATAAAAAAAAAAAAAAA")
#     #     _logger.info(data)

#     #     telebirr_url='http://196.189.44.60:8069/telebirr/ussd/send_sms'
#     #     response = requests.post(telebirr_url, json=data, headers=headers)
#     #     _logger.info("555555555555555555")
#     #     lod_json = json.loads(response.text)
#     #     print("LOAD JSooooooOM")
#     #     print(lod_json['result'])
    

#     #     if lod_json['result'] == 'USSD Sent Successfully':
#     #         msg = 'Success'
#     #     else: msg = 'Failure'

#     #     response = {
#     #             'response': lod_json['result'],
#     #             'msg': msg,
#     #             'trace_no': data['traceNo']
#     #     }
#     #     print(response)
#     #     return response

  
#     # @http.route('/find_pay_confirmed_telebirr', type='json', auth='public', csrf=False)
#     # def find_pay_confirmed_telebirr(self):
#     #     response= {
#     #                 'msg': 'Successs',
#     #                 'status': 'true'
#     #             }
#     #     print("PPPPPPPPPP")
#     #     print(response)
#     #     return response
#     # @http.route('/find_pay_confirmed_telebirr', type='json', auth='public', csrf=False)
#     # def find_pay_confirmed_telebirr(self, id):
#     #     pos_ses = self.env['pos.config'].search([('id', '=', id)])
#     #     if pos_ses.telebirr_payment:
#     #         if pos_ses.telebirr_payment.pay_confirmed == 'confirmed':
#     #             return {
#     #                 'msg': 'Success'
#     #                    }
#     #         elif pos_ses.telebirr_payment.pay_confirmed == 'failed':
#     #             return {
#     #                 'msg': 'Failed'
#     #                    }
#     #     else:
#     #         return {
#     #             'msg': 'Failed'
#     #                }
#     @http.route('/confirm_payment', type='json', auth='public', csrf=False)
#     def confirm_payment(self, **kwargs):
#         post = request.jsonrequest
    
#         print(post, 'POST')
#         telebirr_pay = request.env['telebirr.payment'].sudo().search([('trace_no', '=', post['trace_no'])])

#         if post['msg'] == 'Confirmed':
#             telebirr_pay.pay_confirmed = 'confirmed'
#         elif post['msg'] == 'Failed':
#             telebirr_pay.pay_confirmed = 'failed'

#     @http.route('/send_request_trace_no', type='json', auth='public', csrf=False)
#     def send_request_trace_no(self, data):
#         headers = {'Content-Type': 'application/json'}
#         pay_meth = self.env['pos.payment.method'].search([('id', '=', data['payment_method'])])
#         if pay_meth:
#             response = requests.post('http://196.189.44.60:8069/telebirr/ussd/local_query', json=data, headers=headers)
#             lod_json = json.loads(response.text)
#             amount = round(data['amount'], 2)
#             print(lod_json, 'JSON', amount)
#             if lod_json['result'] == 'could not find':
#                 return {
#                     'msg': 'failed',
#                     'longMsg': 'Trace Number Not Found'
#                 }
#             else:
#                 if lod_json['result']['msg'] == 'pending' and lod_json['result']['amount'] == amount:
#                     return {
#                         'msg': 'pending',
#                         'longMsg': 'Transaction is not Completed',
#                     }
#                 elif lod_json['result']['msg'] == 'confiremed' and lod_json['result']['amount'] == amount:
#                     return {
#                         'msg': 'Success',
#                         'longMsg': 'Transaction is Completed',
#                     }
#                 elif lod_json['result']['msg'] == 'failed' and lod_json['result']['amount'] == amount:
#                     return {
#                         'msg': 'failed',
#                         'longMsg': 'Transaction has Failed',
#                     }
#                 elif lod_json['result']['amount'] != amount:
#                     return {
#                         'msg': 'failed',
#                         'longMsg': 'The price is incorrect',
#                     }

#         else:
#             return {
#                 'longMsg': 'No Payment Method Found'
#         }




