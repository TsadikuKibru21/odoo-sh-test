from odoo import http
import json
import logging
from werkzeug.utils import redirect
from odoo.http import request

_logger = logging.getLogger(__name__)

class TelebirrPaymentController(http.Controller):
    _return_url = '/api/telebirr/payment'

    @http.route('/api/telebirr/payment', type='http', auth='public', methods=['POST'], csrf=False)
    def process_payment(self, **payload):
        try:
            _logger.info("################################## Telebirr Callback Triggered ##################")
            jsondata = json.loads(http.request.httprequest.data)
            _logger.info("Callback Data Received: %s", jsondata)

            trace_no = jsondata.get('trace_no')
            msg = jsondata.get('msg')

            transaction = http.request.env['payment.transaction'].sudo().search([
                ('reference', '=', trace_no)  # Search using reference
            ], limit=1)

            if not transaction:
                _logger.warning(f"Transaction not found for reference: {trace_no}")
                return {'status': 'error', 'message': 'Transaction not found'}

            if msg == 'Confirmed':
                _logger.info("Message Confirmed. Updating transaction state to 'done'.")
                transaction.sudo().write({'state': 'done'})
                return redirect('/payment/status?status=success')
            elif msg == 'Failed':
                _logger.info("Message Failed. Updating transaction state to 'cancel'.")
                transaction.sudo().write({'state': 'cancel'})
                return redirect('/payment/status?status=failed')
                

            _logger.warning("Message status not recognized.")
            return {'status': 'error', 'message': 'Unrecognized status'}

        except Exception as e:
            _logger.error(f"Error processing payment: {e}")
            return {'status': 'error', 'message': str(e)}




class PaymentStatusController(http.Controller):
    @http.route('/payment/custom_status', type='http',methods=['GET'],auth='public', website=True)
    def payment_status(self):
        _logger.info("############################# called 0000000000000000000 ")
        # _logger.info(self)
        # if reference:
        #     # Fetch the transaction using the reference
        #     _logger.info("############################# called")
        #     transaction = http.request.env['payment.transaction'].sudo().search([
        #         ('reference', '=', reference)
        #     ], limit=1)
            
        #     if transaction:
        #         if transaction.state == 'done':
        #             return redirect('/payment/status?status=success')
        #         elif transaction.state == 'cancel':
        #             return redirect('/payment/status?status=failed')
        
        # Default fallback
        return redirect('/payment/status')

class PaymentTelebirrController(http.Controller):

    @http.route('/payment/telebirr/update_phone', type='json', auth='user')
    def update_telebirr_phone(self, phone_number):
        # Get the current user (partner)
        user = request.env.user
        partner = user.partner_id
        if partner:
              partner.write({'telebirr_phone_number': phone_number})
              request.env.cr.commit()  # Explicitly commit the transaction
              request.env.cr.flush()  # Ensure changes are reflected

              _logger.info("########## telebirr_phone_number updated ############")
              _logger.info(phone_number)
              return {"status":"success"}


        # Update the telebirr_phone_number field with the phone number
     
