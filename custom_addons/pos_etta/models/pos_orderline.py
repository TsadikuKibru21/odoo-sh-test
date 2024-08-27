from odoo import fields, models, api, _

from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_repr, float_compare
import json
import logging
from datetime import datetime
from odoo.tools import (float_compare, float_repr, formatLang)

_logger = logging.getLogger(__name__)

# class AccountTax(models.Model):
#     _inherit = 'account.tax'
    
#     @api.model
#     def _prepare_tax_totals(self, base_lines, currency, tax_lines=None, is_company_currency_requested=False):
#         """ Compute the tax totals details for the business documents. """
#         #_logger.info("=================== Called _prepare_tax_totals ===================")
#         #_logger.info("Input base_lines: %s", base_lines)
#         #_logger.info("currency: %s", currency)
#         #_logger.info("tax_lines: %s", tax_lines)
#         #_logger.info("is_company_currency_requested: %s", is_company_currency_requested)

#         # ==== Compute the taxes ====

#         to_process = []
#         for base_line in base_lines:
#             to_update_vals, tax_values_list = self._compute_taxes_for_single_line(base_line)
#             #_logger.info("Processed base_line: %s", base_line)
#             #_logger.info("to_update_vals: %s", to_update_vals)
#             #_logger.info("tax_values_list: %s", tax_values_list)
#             to_process.append((base_line, to_update_vals, tax_values_list))

#         def grouping_key_generator(base_line, tax_values):
#             source_tax = tax_values['tax_repartition_line'].tax_id
#             return {'tax_group': source_tax.tax_group_id}

#         global_tax_details = self._aggregate_taxes(to_process, grouping_key_generator=grouping_key_generator)
#         #_logger.info("global_tax_details: %s", global_tax_details)

#         tax_group_vals_list = []
#         for tax_detail in global_tax_details['tax_details'].values():
#             tax_group_vals = {
#                 'tax_group': tax_detail['tax_group'],
#                 'base_amount': tax_detail['base_amount_currency'],
#                 'tax_amount': tax_detail['tax_amount_currency'],
#             }
#             if is_company_currency_requested:
#                 tax_group_vals['base_amount_company_currency'] = tax_detail['base_amount']
#                 tax_group_vals['tax_amount_company_currency'] = tax_detail['tax_amount']

#             # Handle a manual edition of tax lines.
#             if tax_lines is not None:
#                 matched_tax_lines = [
#                     x
#                     for x in tax_lines
#                     if x['tax_repartition_line'].tax_id.tax_group_id == tax_detail['tax_group']
#                 ]
#                 if matched_tax_lines:
#                     tax_group_vals['tax_amount'] = sum(x['tax_amount'] for x in matched_tax_lines)

#             #_logger.info("Appended tax_group_vals: %s", tax_group_vals)
#             tax_group_vals_list.append(tax_group_vals)

#         tax_group_vals_list = sorted(tax_group_vals_list, key=lambda x: (x['tax_group'].sequence, x['tax_group'].id))
#         #_logger.info("Sorted tax_group_vals_list: %s", tax_group_vals_list)

#         # ==== Partition the tax group values by subtotals ====

#         amount_untaxed = global_tax_details['base_amount_currency']
#         amount_tax = 0.0

#         amount_untaxed_company_currency = global_tax_details['base_amount']
#         amount_tax_company_currency = 0.0

#         subtotal_order = {}
#         groups_by_subtotal = defaultdict(list)
#         for tax_group_vals in tax_group_vals_list:
#             tax_group = tax_group_vals['tax_group']

#             subtotal_title = tax_group.preceding_subtotal or _("Untaxed Amount")
#             sequence = tax_group.sequence

#             subtotal_order[subtotal_title] = min(subtotal_order.get(subtotal_title, float('inf')), sequence)
#             groups_by_subtotal[subtotal_title].append({
#                 'group_key': tax_group.id,
#                 'tax_group_id': tax_group.id,
#                 'tax_group_name': tax_group.name,
#                 'tax_group_amount': tax_group_vals['tax_amount'],
#                 'tax_group_base_amount': tax_group_vals['base_amount'],
#                 'formatted_tax_group_amount': formatLang(self.env, tax_group_vals['tax_amount'], currency_obj=currency),
#                 'formatted_tax_group_base_amount': formatLang(self.env, tax_group_vals['base_amount'], currency_obj=currency),
#             })
#             #_logger.info("Updated groups_by_subtotal for %s: %s", subtotal_title, groups_by_subtotal[subtotal_title])
#             if is_company_currency_requested:
#                 groups_by_subtotal[subtotal_title][-1]['tax_group_amount_company_currency'] = tax_group_vals['tax_amount_company_currency']
#                 groups_by_subtotal[subtotal_title][-1]['tax_group_base_amount_company_currency'] = tax_group_vals['base_amount_company_currency']

#         # ==== Build the final result ====

#         subtotals = []
#         for subtotal_title in sorted(subtotal_order.keys(), key=lambda k: subtotal_order[k]):
#             amount_total = amount_untaxed + amount_tax
#             subtotals.append({
#                 'name': subtotal_title,
#                 'amount': amount_total,
#                 'formatted_amount': formatLang(self.env, amount_total, currency_obj=currency),
#             })
#             if is_company_currency_requested:
#                 subtotals[-1]['amount_company_currency'] = amount_untaxed_company_currency + amount_tax_company_currency
#                 amount_tax_company_currency += sum(x['tax_group_amount_company_currency'] for x in groups_by_subtotal[subtotal_title])

#             amount_tax += sum(x['tax_group_amount'] for x in groups_by_subtotal[subtotal_title])
#             #_logger.info("Updated subtotals for %s: %s", subtotal_title, subtotals[-1])

#         amount_tax = global_tax_details['tax_amount']
#         #_logger.info("amount_tax: %s", amount_tax)
#         #_logger.info("amount_untaxed: %s", amount_untaxed)
#         amount_total = amount_untaxed + amount_tax
#         #_logger.info("amount_total: %s", amount_total)

#         display_tax_base = (len(global_tax_details['tax_details']) == 1 and currency.compare_amounts(tax_group_vals_list[0]['base_amount'], amount_untaxed) != 0)\
#                         or len(global_tax_details['tax_details']) > 1

#         result = {
#             'amount_untaxed': currency.round(amount_untaxed) if currency else amount_untaxed,
#             'amount_total': currency.round(amount_total) if currency else amount_total,
#             'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=currency),
#             'formatted_amount_untaxed': formatLang(self.env, amount_untaxed, currency_obj=currency),
#             'groups_by_subtotal': groups_by_subtotal,
#             'subtotals': subtotals,
#             'subtotals_order': sorted(subtotal_order.keys(), key=lambda k: subtotal_order[k]),
#             'display_tax_base': display_tax_base
#         }
#         _logger.info("=================== Exiting _prepare_tax_totals ===================")
#         _logger.info("Result: %s", result)
        
#         return result

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    pos_order_id = fields.Many2one('pos.order', string='POS Order', help='Reference to the POS order')
    # service_charge = fields.Float(string='Service Charge')
    service_charge = fields.Many2one('account.tax', string='Service Charge', help='Reference to the service charge tax')
    is_refund = fields.Boolean(string="Is Refund", help="Is a Refund Order")
    fs_no = fields.Char('FS No')
    rf_no = fields.Char('RF No')
    fiscal_mrc = fields.Char('MRC')
    payment_qr_code_str = fields.Char('Payment QR Code')
    

    # @api.depends(
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.balance',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state',
    #     'line_ids.full_reconcile_id',
    #     'state')
    # def _compute_amount(self):
    #     for move in self:
    #         total_untaxed, total_untaxed_currency = 0.0, 0.0
    #         total_tax, total_tax_currency = 0.0, 0.0
    #         total_residual, total_residual_currency = 0.0, 0.0
    #         total, total_currency = 0.0, 0.0

    #         _logger.info("=================== Computing amounts for move: %s ===================", move.id)

    #         for line in move.line_ids:
    #             _logger.info("Processing line: %s, display_type: %s, balance : %s, amount_currency: %s, amount_residual: %s, amount_residual_currency: %s, service_charge: %s",
    #                         line.id, line.display_type, line.balance, line.amount_currency, line.amount_residual, line.amount_residual_currency, line.service_charge_rate)

    #             # Apply the service charge
    #             service_charge = line.balance * line.service_charge_rate
    #             amount_with_service_charge = line.balance + service_charge
    #             amount_currency_with_service_charge = line.amount_currency + (line.amount_currency * line.service_charge_rate)

    #             if move.is_invoice(True):
    #                 # === Invoices ===
    #                 if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
    #                     # Tax amount.
    #                     total_tax += line.balance
    #                     total_tax_currency += line.amount_currency
    #                     total += amount_with_service_charge
    #                     total_currency += amount_currency_with_service_charge
    #                     _logger.info("Updated tax amounts: total_tax: %s, total_tax_currency: %s, total: %s, total_currency: %s",
    #                                 total_tax, total_tax_currency, total, total_currency)
    #                 elif line.display_type in ('product', 'rounding'):
    #                     # Untaxed amount.
    #                     total_untaxed += line.balance
    #                     total_untaxed_currency += line.amount_currency
    #                     total += amount_with_service_charge
    #                     total_currency += amount_currency_with_service_charge
    #                     _logger.info("Updated untaxed amounts: total_untaxed: %s, total_untaxed_currency: %s, total: %s, total_currency: %s",
    #                                 total_untaxed, total_untaxed_currency, total, total_currency)
    #                 elif line.display_type == 'payment_term':
    #                     # Residual amount.
    #                     total_residual += line.amount_residual
    #                     total_residual_currency += line.amount_residual_currency
    #                     _logger.info("Updated residual amounts: total_residual: %s, total_residual_currency: %s",
    #                                 total_residual, total_residual_currency)
    #             else:
    #                 # === Miscellaneous journal entry ===
    #                 if line.debit:
    #                     total += amount_with_service_charge
    #                     total_currency += amount_currency_with_service_charge
    #                     _logger.info("Updated miscellaneous journal entry amounts: total: %s, total_currency: %s",
    #                                 total, total_currency)

    #         sign = move.direction_sign
    #         move.amount_untaxed = sign * total_untaxed_currency
    #         move.amount_tax = sign * total_tax_currency
    #         move.amount_total = sign * total_currency
    #         move.amount_residual = -sign * total_residual_currency
    #         move.amount_untaxed_signed = -total_untaxed
    #         move.amount_tax_signed = -total_tax
    #         move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
    #         move.amount_residual_signed = total_residual
    #         move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(sign * move.amount_total)

    #         _logger.info("Computed amounts for move %s: amount_untaxed: %s, amount_tax: %s, amount_total: %s, amount_residual: %s, amount_untaxed_signed: %s, amount_tax_signed: %s, amount_total_signed: %s, amount_residual_signed: %s, amount_total_in_currency_signed: %s",
    #                     move.id, move.amount_untaxed, move.amount_tax, move.amount_total, move.amount_residual, move.amount_untaxed_signed, move.amount_tax_signed, move.amount_total_signed, move.amount_residual_signed, move.amount_total_in_currency_signed)


    # @api.depends(
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.balance',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state',
    #     'line_ids.full_reconcile_id',
    #     'state')
    # def _compute_amount(self):
    #     for move in self:
    #         total_untaxed, total_untaxed_currency = 0.0, 0.0
    #         total_tax, total_tax_currency = 0.0, 0.0
    #         total_residual, total_residual_currency = 0.0, 0.0
    #         total, total_currency = 0.0, 0.0

    #         _logger.info("=================== Computing amounts for move: %s ===================", move.id)

    #         for line in move.line_ids:
    #             _logger.info("Processing line: %s, display_type: %s, balance : %s, amount_currency: %s, amount_residual: %s, amount_residual_currency: %s, service_charge: %s",
    #                         line.id, line.display_type, line.balance, line.amount_currency, line.amount_residual, line.amount_residual_currency, line.service_charge)

    #             if move.is_invoice(True):
    #                 # === Invoices ===
    #                 if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
    #                     # Tax amount.
    #                     total_tax += line.balance
    #                     total_tax_currency += line.amount_currency
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                     _logger.info("Updated tax amounts: total_tax: %s, total_tax_currency: %s, total: %s, total_currency: %s",
    #                                 total_tax, total_tax_currency, total, total_currency)
    #                 elif line.display_type in ('product', 'rounding'):
    #                     # Untaxed amount.
    #                     total_untaxed += line.balance
    #                     total_untaxed_currency += line.amount_currency
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                     _logger.info("Updated untaxed amounts: total_untaxed: %s, total_untaxed_currency: %s, total: %s, total_currency: %s",
    #                                 total_untaxed, total_untaxed_currency, total, total_currency)
    #                 elif line.display_type == 'payment_term':
    #                     # Residual amount.
    #                     total_residual += line.amount_residual
    #                     total_residual_currency += line.amount_residual_currency
    #                     _logger.info("Updated residual amounts: total_residual: %s, total_residual_currency: %s",
    #                                 total_residual, total_residual_currency)
    #             else:
    #                 # === Miscellaneous journal entry ===
    #                 if line.debit:
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                     _logger.info("Updated miscellaneous journal entry amounts: total: %s, total_currency: %s",
    #                                 total, total_currency)

    #         sign = move.direction_sign
    #         move.amount_untaxed = sign * total_untaxed_currency
    #         move.amount_tax = sign * total_tax_currency
    #         move.amount_total = sign * total_currency
    #         move.amount_residual = -sign * total_residual_currency
    #         move.amount_untaxed_signed = -total_untaxed
    #         move.amount_tax_signed = -total_tax
    #         move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
    #         move.amount_residual_signed = total_residual
    #         move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(sign * move.amount_total)

    #         _logger.info("Computed amounts for move %s: amount_untaxed: %s, amount_tax: %s, amount_total: %s, amount_residual: %s, amount_untaxed_signed: %s, amount_tax_signed: %s, amount_total_signed: %s, amount_residual_signed: %s, amount_total_in_currency_signed: %s",
    #                     move.id, move.amount_untaxed, move.amount_tax, move.amount_total, move.amount_residual, move.amount_untaxed_signed, move.amount_tax_signed, move.amount_total_signed, move.amount_residual_signed, move.amount_total_in_currency_signed)


    # @api.depends_context('lang')
    # @api.depends(
    #     'invoice_line_ids.currency_rate',
    #     'invoice_line_ids.tax_base_amount',
    #     'invoice_line_ids.tax_line_id',
    #     'invoice_line_ids.price_total',
    #     'invoice_line_ids.price_subtotal',
    #     'invoice_payment_term_id',
    #     'partner_id',
    #     'currency_id',
    # )
    # def _compute_tax_totals(self):
    #     """ Computed field used for custom widget's rendering.
    #         Only set on invoices.
    #     """
    #     for move in self:
    #         if move.is_invoice(include_receipts=True):
    #             base_lines = move.invoice_line_ids.filtered(lambda line: line.display_type == 'product')

    #             base_line_values_list = [line._convert_to_tax_base_line_dict() for line in base_lines]

    #             sign = move.direction_sign
    #             if move.id:
    #                 base_line_values_list += [
    #                     {
    #                         **line._convert_to_tax_base_line_dict(),
    #                         'handle_price_include': False,
    #                         'quantity': 1.0,
    #                         'price_unit': sign * line.amount_currency,
    #                     }
    #                     for line in move.line_ids.filtered(lambda line: line.display_type == 'epd')
    #                 ]

    #             kwargs = {
    #                 'base_lines': base_line_values_list,
    #                 'currency': move.currency_id or move.journal_id.currency_id or move.company_id.currency_id,
    #             }

    #             if move.id:
    #                 kwargs['tax_lines'] = [
    #                     line._convert_to_tax_line_dict()
    #                     for line in move.line_ids.filtered(lambda line: line.display_type == 'tax')
    #                 ]
    #             else:
    #                 epd_aggregated_values = {}
    #                 for base_line in base_lines:
    #                     if not base_line.epd_needed:
    #                         continue
    #                     for grouping_dict, values in base_line.epd_needed.items():
    #                         epd_values = epd_aggregated_values.setdefault(grouping_dict, {'price_subtotal': 0.0})
    #                         epd_values['price_subtotal'] += values['price_subtotal']

    #                 for grouping_dict, values in epd_aggregated_values.items():
    #                     taxes = None
    #                     if grouping_dict.get('tax_ids'):
    #                         taxes = self.env['account.tax'].browse(grouping_dict['tax_ids'][0][2])

    #                     kwargs['base_lines'].append(self.env['account.tax']._convert_to_tax_base_line_dict(
    #                         None,
    #                         partner=move.partner_id,
    #                         currency=move.currency_id,
    #                         taxes=taxes,
    #                         price_unit=values['price_subtotal'],
    #                         quantity=1.0,
    #                         account=self.env['account.account'].browse(grouping_dict['account_id']),
    #                         analytic_distribution=values.get('analytic_distribution'),
    #                         price_subtotal=values['price_subtotal'],
    #                         is_refund=move.move_type in ('out_refund', 'in_refund'),
    #                         handle_price_include=False,
    #                         extra_context={'_extra_grouping_key_': 'epd'},
    #                     ))

    #             kwargs['is_company_currency_requested'] = move.currency_id != move.company_id.currency_id

    #             # Compute tax totals
    #             tax_totals = self.env['account.tax']._prepare_tax_totals(**kwargs)

    #             # Log the tax_totals values before assigning them
    #             _logger.info(f"------------------- Tax Totals -------------------")
    #             for key, value in tax_totals.items():
    #                 _logger.info(f"{key}: {value}")

    #             # Log the value of groups_by_subtotal
    #             _logger.info(f"------------------- Groups by Subtotal -------------------")
    #             for subtotal, groups in tax_totals.get('groups_by_subtotal', {}).items():
    #                 _logger.info(f"Subtotal: {subtotal}")
    #                 for group in groups:
    #                     _logger.info(f"  Tax Group Name: {group['tax_group_name']}, Tax Group Amount: {group['tax_group_amount']}, Tax Group Base Amount: {group['tax_group_base_amount']}")

    #             # Log the amount by each tax group name
    #             amount_by_group = {}
    #             for groups in tax_totals.get('groups_by_subtotal', {}).values():
    #                 for group in groups:
    #                     tax_group_name = group['tax_group_name']
    #                     tax_group_amount = group['tax_group_amount']
    #                     if tax_group_name in amount_by_group:
    #                         amount_by_group[tax_group_name] += tax_group_amount
    #                     else:
    #                         amount_by_group[tax_group_name] = tax_group_amount

    #             _logger.info(f"------------------- Amount by Tax Group -------------------")
    #             for tax_group_name, amount in amount_by_group.items():
    #                 _logger.info(f"Tax Group Name: {tax_group_name}, Amount: {amount}")

    #             move.tax_totals = tax_totals

    #             if move.invoice_cash_rounding_id:
    #                 rounding_amount = move.invoice_cash_rounding_id.compute_difference(move.currency_id, move.tax_totals['amount_total'])
    #                 totals = move.tax_totals
    #                 totals['display_rounding'] = True
    #                 if rounding_amount:
    #                     if move.invoice_cash_rounding_id.strategy == 'add_invoice_line':
    #                         totals['rounding_amount'] = rounding_amount
    #                         totals['formatted_rounding_amount'] = formatLang(self.env, totals['rounding_amount'], currency_obj=move.currency_id)
    #                     elif move.invoice_cash_rounding_id.strategy == 'biggest_tax':
    #                         if totals['subtotals_order']:
    #                             max_tax_group = max((
    #                                 tax_group
    #                                 for tax_groups in totals['groups_by_subtotal'].values()
    #                                 for tax_group in tax_groups
    #                             ), key=lambda tax_group: tax_group['tax_group_amount'])
    #                             max_tax_group['tax_group_amount'] += rounding_amount
    #                             max_tax_group['formatted_tax_group_amount'] = formatLang(self.env, max_tax_group['tax_group_amount'], currency_obj=move.currency_id)
    #                     totals['amount_total'] += rounding_amount
    #                     totals['formatted_amount_total'] = formatLang(self.env, totals['amount_total'], currency_obj=move.currency_id)
    #         else:
    #             move.tax_totals = None
   
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # service_charge = fields.Float(string='Service Charge')
    
    # @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id', 'service_charge')
    # def _compute_totals(self):
    #     for line in self:
    #         if line.display_type != 'product':
    #             line.price_total = line.price_subtotal = False
    #         # Compute 'price_subtotal'. 
    #         line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
    #         line_service_charge_price_unit = line_discount_price_unit * (1 + (line.service_charge / 100.0))
    #         subtotal = line.quantity * line_service_charge_price_unit
    #         # Compute 'price_total'.            
    #         if line.tax_ids:
    #             taxes_res = line.tax_ids.compute_all(
    #                 line_service_charge_price_unit,
    #                 quantity=line.quantity,
    #                 currency=line.currency_id,
    #                 product=line.product_id,
    #                 partner=line.partner_id,
    #                 is_refund=line.is_refund,
    #             )
    #             line.price_subtotal = taxes_res['total_excluded']
    #             line.price_total = taxes_res['total_included']
    #         else:
    #             line.price_total = line.price_subtotal = subtotal
    
    # def _convert_to_tax_base_line_dict(self, **kwargs):
    #     # Call the original function with the required arguments
    #     tax_base_line_dict = super(AccountMoveLine, self)._convert_to_tax_base_line_dict(**kwargs)
    #     # Add the service charge to the price_unit
    #     service_charge = self.service_charge or 0.0
    #     tax_base_line_dict['service_charge'] = service_charge
    #     # tax_base_line_dict['price_unit'] = self.price_unit * (1 + service_charge / 100.0)
        
    #     return tax_base_line_dict

class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    is_refund = fields.Boolean(string="Is Refund", help="Is a Refund Order")
    checked = fields.Boolean(string="Checked Cash", help="Cash received from waiter")
    waiter_name = fields.Char('Waiter Name')
    fs_no = fields.Char('FS No')
    rf_no = fields.Char('RF No')
    ej_checksum = fields.Char('EJ Checksum')
    fiscal_mrc = fields.Char('MRC')
    payment_qr_code_str = fields.Char('Payment QR Code')
    # service_charge_amount = fields.Monetary(string='Service Charge', readonly=True, compute='_compute_service_charge_amount', group_operator='sum')
    synced_mrc = fields.Text(string='Synced MRC')
    synced_mrc_list = fields.Char(compute='_convert_synced_mrc_to_list', inverse='_convert_synced_mrc_to_text')

    @api.model
    def set_order_checked(self, order_id):
        order = self.search([('pos_reference', '=', order_id)], limit=1)
        if order:
            order.update({
                'checked': True
            })
            return True
        return False
            
    @api.model
    def get_orders_without_fs_no(self, search_string):
        orders = self.search([
            '|', '|', '|',
                ('fs_no', '=', False),
                ('fiscal_mrc', '=', False),
                ('ej_checksum', '=', False),
                ('synced_mrc', '=', False),
            ("amount_total", ">", 0)
        ])
        def string_not_in_synced_mrc(order):
            synced_mrc_list = json.loads(order.synced_mrc or '[]')
            return search_string not in synced_mrc_list
        
        filtered_orders = orders.filtered(string_not_in_synced_mrc)
        
        return filtered_orders.mapped('pos_reference')

    @api.model
    def get_orders_without_rf_no(self, search_string):
        orders = self.search([
            '|', '|', '|',
                ('rf_no', '=', False),
                ('fiscal_mrc', '=', False),
                ('ej_checksum', '=', False),
                ('synced_mrc', '=', False),
            ("amount_total", ">", 0)
        ])
        def string_not_in_synced_mrc(order):
            synced_mrc_list = json.loads(order.synced_mrc or '[]')
            return search_string not in synced_mrc_list
        
        filtered_orders = orders.filtered(string_not_in_synced_mrc)
        
        return filtered_orders.mapped('pos_reference')
    
    @api.model
    def add_to_synced_mrc(self, pos_reference, fiscal_mrc):
        orders = self.search([('pos_reference', '=', pos_reference)])
        for order in orders:
            synced_mrc_list = json.loads(order.synced_mrc or '[]')
            if fiscal_mrc not in synced_mrc_list:
                synced_mrc_list.append(fiscal_mrc)
                order.synced_mrc = json.dumps(synced_mrc_list)

    @api.model
    def _convert_synced_mrc_to_list(self):
        for order in self:
            if order.synced_mrc:
                order.synced_mrc_list = json.loads(order.synced_mrc)

    @api.model
    def _convert_synced_mrc_to_text(self):
        for order in self:
            if order.synced_mrc_list:
                order.synced_mrc = json.dumps(order.synced_mrc_list)

    @api.model
    def _process_order(self, order, draft, existing_order):
        result = super(PosOrderInherit, self)._process_order(order, draft, existing_order)
        pos_order = self.search([('id', '=', result)])
        mrp_order = self.env['mrp.production']
        # Check if the pos_order.is_refund field exists and if it exists, only proceed if it is False
        if pos_order.config_id.create_mrp_order and draft == False:
            for line in pos_order.lines:
                route_ids = line.product_id.route_ids.mapped('name')
                if 'Manufacture' in route_ids:
                    if line.product_id.bom_ids and line.qty > 0:
                        mrp_order = mrp_order.create({
                            'product_id': line.product_id.id,
                            'product_qty': line.qty,
                            'date_start': datetime.now(),
                            'user_id': self.env.user.id,
                            'company_id': self.env.company.id,
                            'origin': pos_order.pos_reference
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
            
    @api.model
    def _order_fields(self, ui_order):
        vals = super(PosOrderInherit, self)._order_fields(ui_order)
        vals.update({
            'is_refund': ui_order.get('is_refund', False),
            'checked': ui_order.get('checked', False),
            'fs_no': ui_order.get('fs_no', ''),
            'rf_no': ui_order.get('rf_no', ''),
            'ej_checksum': ui_order.get('ej_checksum', ''),
            'fiscal_mrc': ui_order.get('fiscal_mrc', ''),
            'payment_qr_code_str': ui_order.get('payment_qr_code_str', ''),
        })

        return vals
    
    def _prepare_refund_values(self, current_session):
        vals = super(PosOrderInherit, self)._prepare_refund_values(current_session)
        vals.update({'is_refund': True})
        return vals

    def _prepare_invoice_vals(self):
        result = super(PosOrderInherit, self)._prepare_invoice_vals()
        result.update({
            'pos_order_id': self.id,
            'invoice_date' : self.date_order,
            'ref': self.pos_reference,
            'fs_no':self.fs_no,
            'is_refund': self.is_refund,
            'rf_no':self.rf_no,
            'fiscal_mrc':self.fiscal_mrc,
            'payment_qr_code_str': self.payment_qr_code_str,
        })
        return result

    def _export_for_ui(self, order):
        result = super(PosOrderInherit, self)._export_for_ui(order)
        result.update({
            'is_refund': order.is_refund,
            'checked': order.checked,
            'fs_no': order.fs_no,
            'rf_no': order.rf_no,
            'ej_checksum': order.ej_checksum,
            'fiscal_mrc': order.fiscal_mrc,
            'payment_qr_code_str': order.payment_qr_code_str,
        })
        return result

class PosOrderLineInherit(models.Model):
    _inherit = 'pos.order.line'

    service_charge = fields.Many2one('account.tax', string='Service Charge', domain=[('type_tax_use', '=', 'sale'), ('include_base_amount', '=', True)], help='Reference to the service charge tax')
    
    def _export_for_ui(self, orderline):
        return {
            'id': orderline.id,
            'qty': orderline.qty,
            'attribute_value_ids': orderline.attribute_value_ids.ids,
            'custom_attribute_value_ids': orderline.custom_attribute_value_ids.read(['id', 'name', 'custom_product_template_attribute_value_id', 'custom_value'], load=False),
            'price_unit': orderline.price_unit,
            'skip_change': orderline.skip_change,
            'uuid': orderline.uuid,
            'price_subtotal': orderline.price_subtotal,
            'price_subtotal_incl': orderline.price_subtotal_incl,
            'product_id': orderline.product_id.id,
            'discount': orderline.discount,
            'tax_ids': [[6, False, orderline.tax_ids.mapped(lambda tax: tax.id)]],
            'pack_lot_ids': [[0, 0, lot] for lot in orderline.pack_lot_ids.export_for_ui()],
            'customer_note': orderline.customer_note,
            'refunded_qty': orderline.refunded_qty,
            'price_extra': orderline.price_extra,
            'full_product_name': orderline.full_product_name,
            'refunded_orderline_id': orderline.refunded_orderline_id.id,
            'combo_parent_id': orderline.combo_parent_id.id,
            'combo_line_ids': orderline.combo_line_ids.mapped('id'),
            'service_charge': orderline.service_charge,  # Add the service charge here
        }