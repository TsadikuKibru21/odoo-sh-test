from odoo.http import request
from odoo import http

import logging

_logger = logging.getLogger(__name__)

class OrderPrinterController(http.Controller):
    @http.route('/create_void_reason', type='json', auth='public', csrf=False)
    def create_resource_endpoint(self, **kw):
        try:
            request.env['voided.orders'].create({
                'order_id': kw.get("order_id"),
                'cashier': kw.get("cashier"),
                'product': kw.get("product"),
                'unit_price': kw.get("unit_price"),
                'quantity': kw.get("quantity"),
                'reason_id': kw.get("reason_id"),
            })
            return True
        except Exception as e:
            # Optionally log the exception here
            _logger.info(e)
            return False