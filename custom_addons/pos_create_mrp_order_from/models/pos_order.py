# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
import datetime
import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
	_inherit = 'pos.order'

	@api.model
	def _process_order(self, order, draft, existing_order):
		result = super(PosOrder, self)._process_order(order, draft, existing_order)
		pos_order = self.search([('id', '=', result)])
		mrp_order = self.env['mrp.production']
		# Check if the pos_order.is_refund field exists and if it exists, only proceed if it is False
		if pos_order.config_id.create_mrp_order:
			for line in pos_order.lines:
				route_ids = line.product_id.route_ids.mapped('name')
				if 'Manufacture' in route_ids:
					if line.product_id.bom_ids and line.qty > 0:
						mrp_order = mrp_order.create({
							'product_id': line.product_id.id,
							'product_qty': line.qty,
							'date_start': datetime.datetime.now(),
							'user_id': self.env.user.id,
							'company_id': self.env.company.id,
							# 'pos_order_id': self.id
						})
						mrp_order.action_confirm()
						if pos_order.config_id.is_done:
							mrp_order.write({
								'qty_producing': line.qty,
							})
							for move_line in mrp_order.move_raw_ids:
								move_line.write({'quantity': move_line.product_uom_qty, 'picked': True})
							mrp_order.button_mark_done()
		return result