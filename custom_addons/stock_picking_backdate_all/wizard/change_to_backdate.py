# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
import logging

_logger = logging.getLogger(__name__)

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def _set_scheduled_date(self):
        for picking in self:
            picking.move_ids.write({'date': picking.scheduled_date})

class PickingBackDate(models.TransientModel):
    _name = 'stock.picking.backdate.wiz'
    _description = "Picking Backdate Wizard"

    date = fields.Datetime('Date', default=fields.Datetime.now)
    picking_ids = fields.Many2many('stock.picking')

    def change_to_backdate_wizard(self):
        active_ids = self.env.context.get('active_ids')
        active_record = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id'))

        return {
            'name': 'Backdate Transfer',
            'res_model': 'stock.picking.backdate.wiz',
            'view_mode': 'form',
            'view_id': self.env.ref('stock_picking_backdate_all.stock_picking_backdate_wiz_view_form').id,
            'context': {
                'default_picking_ids': [(6, 0, active_ids)],
            },
            'target': 'new',
            'type': 'ir.actions.act_window'
        }

    def change_to_backdate(self):
        for picking in self.picking_ids:
            move_lines = self.env['stock.move'].search([('picking_id', '=', picking.id)])
            account_moves = self.env['account.move'].search([('stock_move_id', 'in', move_lines.ids)])

            # Set account moves to draft
            for account_move in account_moves:
                account_move.button_draft()
                account_move.name = False
                account_move.date = self.date
                account_move.action_post()

            # Update stock moves
            for move in move_lines:
                move.date = self.date
                valuation_layers = self.env['stock.valuation.layer'].search([('stock_move_id', '=', move.id)])
                for valuation_layer in valuation_layers:
                    _logger.info("==============va==========%s", valuation_layer.create_date)
                    self.env.cr.execute('UPDATE stock_valuation_layer SET create_date=%s WHERE id=%s', (self.date, valuation_layer.id))
                    _logger.info("==============va==========%s", valuation_layer.create_date)

                move_lines = self.env['stock.move.line'].search([('move_id', '=', move.id)])
                for move_line in move_lines:
                    move_line.date = self.date

            # Update picking
            picking.scheduled_date = self.date
            picking.date_done = self.date