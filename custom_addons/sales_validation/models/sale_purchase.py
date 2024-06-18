from odoo import api, fields, models, tools, _
import re
import os
import time
import logging
import datetime
from datetime import timedelta
_logger=logging.getLogger(__name__)
from odoo import api, models

# class ProductTemplate(models.Model):
#     _inherit = 'product.template'

#     local = fields.Boolean(string='Local')

#     @api.model
#     def create(self, vals):
#         if vals.get('local'):
#             five_digits=[]
#             products = self.search([('barcode', '!=', False), ('barcode', '!=', '')])
#             for product in products:
#                 if len(product.barcode)==5:
#                     five_digits.append(product.barcode)

#             if five_digits:
#                 greatest_barcode = max(five_digits)
#             else:
#                 greatest_barcode = None

#             _logger.info("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
#             _logger.info(greatest_barcode)

#             last_product=self.search([('barcode','=',greatest_barcode)],limit=1)
#             _logger.info(last_product.barcode)
#             if last_product:
#                 last_barcode = last_product.barcode
#                 last_barcode_number = int(last_barcode[-5:])
#                 _logger.info(last_barcode_number)
#                 new_barcode_number = last_barcode_number + 1
#                 _logger.info(new_barcode_number)
#             else:
#                 new_barcode_number = 1
#             new_barcode = str(new_barcode_number).zfill(5)
#             _logger.info(new_barcode)
#             vals['barcode'] = new_barcode
#             vals['default_code'] = new_barcode

#         return super(ProductTemplate, self).create(vals)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    local = fields.Boolean(string='Local')

    @api.model
    def generate_barcode(self):
        five_digits=[]
        products = self.search([('barcode', '!=', False), ('barcode', '!=', ''),('local','=',True)])
        for product in products:
            if len(product.barcode)==5:
                five_digits.append(product.barcode)
        if five_digits:
            greatest_barcode = max(five_digits)
        else:
            greatest_barcode = None

        _logger.info("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        _logger.info(greatest_barcode)

        last_product=self.search([('barcode','=',greatest_barcode)],limit=1)
        _logger.info(last_product.barcode)
        if last_product:
            last_barcode = last_product.barcode
            last_barcode_number = int(last_barcode[-5:])
            _logger.info(last_barcode_number)
            new_barcode_number = last_barcode_number + 1
            _logger.info(new_barcode_number)
        else:
            new_barcode_number = 1
        new_barcode = str(new_barcode_number).zfill(5)
        _logger.info(new_barcode)
        return new_barcode

    @api.model
    def create(self, vals):
        if vals.get('local'):
            prod_barcode=self.generate_barcode()
            vals['barcode'] = prod_barcode
            vals['default_code'] = prod_barcode
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        if vals.get('local'):
            prod_barcode=self.generate_barcode()

            vals['barcode'] = prod_barcode
            vals['default_code'] = prod_barcode
        return super(ProductTemplate, self).write(vals)























class SaleOrder(models.Model):
	_inherit = "sale.order"

	# def update_invoice_method(self): 
	# 	app=self.env['sale.order'].search([('state','=','done'),('cashier_id.id','=',1806)])
	# 	bc=0
	# 	for aaa in app:
	# 		invo=aaa.invoice_ids.id
	# 		if invo:
	# 			aaa.x_studio_inv_id=invo
    #             aaa.x_studio_branch="summit"
    #             aaa.x_studio_cashier="tewodaj"
	# 			bc+=1
	# 			if bc>5:
	# 				self.env.cr.commit()
	# 				bc=0
		



		# app=self.env['account.payment'].search([("x_studio_reconcilation_id","=",False)])
		# bc=0
		# for aaa in app:
		# 	try:
		# 		invo=aaa.reconciled_invoice_ids.id
		# 		if invo:
		# 			aaa.x_studio_reconcilation_id=invo
		# 	except:
		# 		pass
		# 	bc+=1
		# 	if bc>5:
		# 		self.env.cr.commit()
		# 		bc=0
		

# class AccountPayment(models.Model):
#     _inherit = 'account.payment'

#     x_studio_brancho= fields.Char(string='Branchoo', compute='_compute_branch_type', store=True)
#     x_studio_cashiero= fields.Char(string='Cashieroo', compute='_compute_cashier_type', store=True)

#     @api.depends('reconciled_invoice_ids')
#     def _compute_branch_type(self):
#         for payment in self:
#             changed = False
#             invoice_id = payment.reconciled_invoice_ids[0].id if payment.reconciled_invoice_ids else False
#             if invoice_id:
#                 invoice = self.env['account.move'].browse(invoice_id)
#                 sale_order = invoice.invoice_origin
#                 sales_ord=self.env['sale.order'].search([('name','=',sale_order)],limit=1)
#                 if sales_ord:
#                     payment.x_studio_brancho = sales_ord.branch_id.name
#                     changed = True
#             if changed == False:
#                     payment.x_studio_brancho = "UNKOWN"


#     @api.depends('reconciled_invoice_ids')
#     def _compute_cashier_type(self):
#         for payment in self:
#             changed = False
#             invoice_id = payment.reconciled_invoice_ids[0].id if payment.reconciled_invoice_ids else False
#             if invoice_id:
#                 invoice = self.env['account.move'].browse(invoice_id)
#                 sale_order = invoice.invoice_origin
#                 sales_ord=self.env['sale.order'].search([('name','=',sale_order)],limit=1)
#                 if sales_ord:
#                     payment.x_studio_cashiero = sales_ord.cashier_id.name
#                     changed = True
#             if changed == False:
#                     payment.x_studio_cashiero = "UNKOWN"
                


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    x_studio_brancho = fields.Char(string='Branchoo', compute='_compute_branch_type')
    x_studio_cashiero = fields.Char(string='Cashieroo', compute='_compute_cashier_type')

    x_studio_branch_update = fields.Char(string='Branch Update')
    x_studio_cashier_update = fields.Char(string='Cashier Update')

    @api.depends('reconciled_invoice_ids')
    def _compute_branch_type(self):
        for payment in self:
            changed = False
            invoice_id = payment.reconciled_invoice_ids[0].id if payment.reconciled_invoice_ids else False
            if invoice_id:
                invoice = self.env['account.move'].browse(invoice_id)
                sale_order = invoice.invoice_origin
                sales_ord = self.env['sale.order'].search([('name', '=', sale_order)], limit=1)
                if sales_ord:
                    payment.x_studio_brancho = sales_ord.branch_id.name
                    changed = True
            if not changed:
                payment.x_studio_brancho = "UNKNOWN"

    @api.depends('reconciled_invoice_ids')
    def _compute_cashier_type(self):
        for payment in self:
            changed = False
            invoice_id = payment.reconciled_invoice_ids[0].id if payment.reconciled_invoice_ids else False
            if invoice_id:
                invoice = self.env['account.move'].browse(invoice_id)
                sale_order = invoice.invoice_origin
                sales_ord = self.env['sale.order'].search([('name', '=', sale_order)], limit=1)
                if sales_ord:
                    payment.x_studio_cashiero = sales_ord.cashier_id.name
                    changed = True
            if not changed:
                payment.x_studio_cashiero = "UNKNOWN"



    # def change_entry_items(self):
    #     find_yetenache_payments=self.search([
    #         ("x_studio_cashier_update","=","HAIMANOT KIBER TEMESGEN"),
    #         ("x_studio_branch_update","=","Summit"),
    #     ])
    #     count=0
    #     for afuk in find_yetenache_payments:
    #         count+=1
    #         # afuk.journal_id=212
    #         find_acc_move=self.env["account.move"].search([("name","=",afuk.name)])
    #         for acc_mv in find_acc_move:
    #             _logger.info("First yetunachoo First 11111111111111")
    #             _logger.info(afuk.name)
    #             acc_mv.journal_id=212 # Apply Change one
    #             _logger.info("Second yetunachoo First 222222222222222")

    #             find_items=self.env["account.move.line"].search([("move_id","=",acc_mv.id),("debit",">",0)])
    #             for item in find_items:
    #                 _logger.info("Third yetunachoo First 33333333333333")

    #                 item.account_id=683 # Apply Change two
    #         _logger.info("Yetenacheeeeeeeeee doooo doo dooo daaa")
    #         _logger.info(afuk.name)
    #         _logger.info(count)


    def change_entry_items(self):
        cr = self.env.cr

        find_yetenache_payments = self.search([
            ("x_studio_cashier_update", "=", "HAIMANOT KIBER TEMESGEN"),
            ("x_studio_branch_update", "=", "Summit")
        ])
        count = 0
        for afuk in find_yetenache_payments:
            count += 1
            find_acc_move = self.env["account.move"].search([("id", "=", afuk.move_id.id)])
            for acc_mv in find_acc_move:
                _logger.info("First yetunachoo First 11111111111111")
                _logger.info(afuk.name)
                cr.execute("UPDATE account_move SET journal_id = 168 WHERE id = %s", (acc_mv.id,)) # Apply Change one
                _logger.info("Second yetunachoo First 222222222222222")

                find_items = self.env["account.move.line"].search([("move_id", "=", acc_mv.id), ("debit", ">", 0)])
                for item in find_items:
                    _logger.info("Third yetunachoo First 33333333333333")

                    cr.execute("UPDATE account_move_line SET account_id = 683 WHERE id = %s", (item.id,)) # Apply Change two
            _logger.info("Yetenacheeeeeeeeee doooo doo dooo daaa")
            _logger.info(afuk.name)
            _logger.info(count)











        # UPDATE account_move  SET journal_id = 212  WHERE name IN (SELECT name FROM account_payment WHERE x_studio_cashier_update = 'HAIMANOT KIBER TEMESGEN' AND x_studio_branch_update = 'Summit');
        # UPDATE account_move_line SET account_id = 683 WHERE debit > 0 AND move_id IN (SELECT id FROM account_move WHERE name IN (SELECT name FROM account_payment WHERE x_studio_cashier_update = 'HAIMANOT KIBER TEMESGEN' AND x_studio_branch_update = 'Summit'));

        # SELECT COUNT(*) FROM account_move WHERE name IN (SELECT name FROM account_payment WHERE x_studio_cashier_update = 'HAIMANOT KIBER TEMESGEN' AND x_studio_branch_update = 'Summit') AND JOURNAL_ID=146;
        # SELECT COUNT(*) FROM account_move_line WHERE debit > 0 AND move_id IN (SELECT id FROM account_move WHERE name IN (SELECT name FROM account_payment WHERE x_studio_cashier_update = 'HAIMANOT KIBER TEMESGEN' AND x_studio_branch_update = 'Summit'));

        # SELECT COUNT(*) FROM account_move am WHERE am.name IN (SELECT am.name FROM account_payment ap WHERE ap.x_studio_cashier_update = 'HAIMANOT KIBER TEMESGEN' AND ap.x_studio_branch_update = 'Summit');


################### Back Date Block ######################
class StockDate(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        super(StockDate, self)._action_done()
        if self.picking_type_code == 'outgoing' and 'Return' not in self.origin:
            self.write({"date": self.sale_id.date_order, "date_done": self.sale_id.date_order})
            self.move_lines.write({"date": self.sale_id.date_order})
            self.move_line_ids.write({"date": self.sale_id.date_order})
            
    def button_validate(self):
        if self.scheduled_date and self.picking_type_code == 'outgoing':
            return super(
                StockDate, self.with_context(force_period_date=self.scheduled_date)
            ).button_validate()           
        else:
            return super(StockDate, self).button_validate()

class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"
    _order = "id"

    create_date = fields.Datetime(related="stock_move_id.date", readonly=False)



##########################################################################
 




class CashierEmployee(models.Model):
    _inherit='hr.employee'

    x_studio_csh_account = fields.Many2one('account.journal', string="Csh Account") 

class AccountPay(models.Model):
    _inherit='account.payment'

    x_studio_sales_payment_type = fields.Char(string="sales payment type")
    x_studio_reconcilation_id = fields.Char(string="reconcilation_id")
    x_studio_payment_method_1= fields.Selection([
        ('cash', 'cash'),
        ('credit','credit'),
        ('visa', 'visa'),
        ('telebirr', 'telebirr'),
        ('amole','amole')
        ],string='Sales Payment Method')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_studio_inv_id=fields.Char(string="Inv id")


    # Sales Validation Block
    def confirm_sale_orders(self):
        mo = self.env['sale.order'].search(
            [("state","=","draft")], order="date_order asc")
        
        count_all = 0
        count = 0
        for m in mo:
            _logger.info(m.name)
            count_all += 1
            count += 1
            _logger.info(m.payment_method)
            _logger.info(m.cashier_id)
            if any(line.product_id.name == 'Expenses' for line in m.order_line):
                continue
            else:               
                if (m.state=='draft' and m.payment_method !='credit' and len(m.cashier_id)!=0) or (m.state=='draft' and m.payment_method=='credit'):
                    try:
                        m.action_confirm()
                    except:
                        pass
                    if count > 3:
                        count = 0
                        self.env.cr.commit()





    def action_confirm(self):
        count = 1        
        ress = super(SaleOrder, self).action_confirm()
        for order in self:

            # warehouse = order.warehouse_id
            # if order.picking_ids:
            #     for picking in order.picking_ids:
            #         picking.action_assign()
            #         picking.action_confirm()
            #         for mv in picking.move_ids_without_package:
            #             mv.quantity_done = mv.product_uom_qty
            #         picking.button_validate()

            order._create_invoices()
            for invoice in order.invoice_ids:
                invoice.action_post()
                if order.payment_method !='credit':
                    j_id = order.cashier_id.x_studio_csh_account.id if order.cashier_id else False
                    
                    if re.match('cash',order.payment_method,re.IGNORECASE):
                        x_studio_payment_method_1='cash'
                    elif re.match('credit',order.payment_method,re.IGNORECASE):
                        x_studio_payment_method_1='credit'
                    elif re.match('visa',order.payment_method,re.IGNORECASE):
                        x_studio_payment_method_1='visa'
                    elif re.match('amole',order.payment_method,re.IGNORECASE):
                        x_studio_payment_method_1='amole'
                    elif re.match('tele',order.payment_method,re.IGNORECASE):
                        x_studio_payment_method_1='telebirr'                    

                    payment_vals = {
                        'date': order.date_order,
                        'amount': invoice.amount_total,
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'journal_id': j_id,
                        'currency_id': 79,
                        'partner_id': invoice.partner_id.id,
                        'partner_bank_id': False,
                        'payment_method_id': 1,
                    }
                    pay = self.env['account.payment'].create(payment_vals)
                    _logger.info("+++++++++*********************+++++++++++****************+++++++++++++***************++++++")
                    pay.write({'x_studio_payment_method_1':x_studio_payment_method_1})
                    pay.action_post()
                    domain = [('account_internal_type', 'in',
                                ('receivable', 'payable')), ('reconciled', '=', False)]
                    payment_lines = pay.line_ids.filtered_domain(domain)
                    for account in payment_lines.account_id:
                        (payment_lines + invoice.line_ids).filtered_domain(
                            [('account_id', '=', account.id), ('reconciled', '=', False)]).reconcile()
            count=count+1
            if count>4:
                self.env.cr.commit()
                _logger.info("++++++++++++++++++ ~~~~~~~~~~~~~~~~~~~~~~~ ++++++++++++++++++++++++++++++")
                count=0
        return ress


    # def update_payment_method(self):
    #     app=self.env['sale.order'].search([('x_studio_inv_id','=',False)])
    #     bc=0
    #     for aaa in app:
    #         invo=aaa.invoice_ids.id
    #         if invo:
    #             aaa.x_studio_inv_id=invo
    #             bc+=1
    #             if bc>5:
    #                 self.env.cr.commit()
    #                 bc=0

class SaleOrderLine(models.Model):
    _inherit='sale.order.line'
    
    remote_id=fields.Char()


class PurchOrder(models.Model):
    _inherit = "purchase.order"

    def action_create_invoice(self):
        res = super(PurchOrder, self).action_create_invoice()
        invoice_id = res['res_id']
        invoice = self.env['account.move'].browse(invoice_id)
        # purchase_receipt_date = self.picking_ids.filtered(lambda p: p.picking_type_code == 'incoming').scheduled_date
        # if purchase_receipt_date:
        #     invoice.invoice_date = purchase_receipt_date.date()
        #     return res
        purchase_receipts = self.picking_ids.filtered(lambda p: p.picking_type_code == 'incoming')
        if purchase_receipts:
            purchase_receipt_date = purchase_receipts[0].scheduled_date
        else:
            # Handle the case when no purchase receipt is found
            purchase_receipt_date = False




class Salesa(models.Model):
    _inherit = "sale.order"

    def identiy_duplicated_order(self):
        cr = self.env.cr
        cr.execute("""
            SELECT s1.name
            FROM sale_order s1
            LEFT JOIN (
                SELECT MIN(id) AS id, name
                FROM sale_order
                GROUP BY name
            ) s2 ON s1.id = s2.id
            WHERE s2.id IS NULL;
        """)
        duplicated_orders = cr.fetchall()
        for dd in duplicated_orders:
            self.env['x_dupa_orders'].create({'x_name': dd[0]})