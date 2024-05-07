from email.policy import default
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class Payment_Request(models.Model):
    _inherit = 'approval.request'

    reciept_id = fields.Many2one('account.move', ondelete='cascade',
                                 string='Related Reciept', help='Reciept Related')

    def action_approve(self, approver=None):
        _logger.info("***************************************")

        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            )
        _logger.info(approver.request_id)
        # _logger.info(approver.request_id.partner_id)
        # return True
        if approver.request_id.category_id.id == 5:
            _logger.info("#################################333")
            _logger.info(approver.user_id.x_studio_approve_payment_max)
            # if approver.request_id.amount > approver.user_id.x_studio_approve_payment_max:
            create_request = False
            _logger.info(approver.request_id.reciept_id)
            approver_list = []
            for each_approver in approver.request_id.approver_ids:
                _logger.info(each_approver.user_id.name)
                _logger.info(each_approver.id)
                approver_list.append({
                    "approver": each_approver,
                    "amount" : each_approver.user_id.x_studio_approve_payment_max
                })
            status_lst = approver.request_id.mapped('approver_ids.status')
               
            number_of_approves =status_lst.count('approved')
            minimal_approvers = len(status_lst)

            # _logger.info(approver_list)
            approver_list = sorted(approver_list, key=lambda d: d['amount']) 
            _logger.info(approver_list)
            if approver.request_id.reciept_id.id == False and number_of_approves == minimal_approvers - 1:
                            create_request = True;
            elif approver.request_id.reciept_id.id == False: 
                for a in approver_list:
                        # each_approver = self.env['approver.approver'].search(["id" , "=" , a.id])
                        _logger.info(a['approver'].id)
                        _logger.info(approver.id)
                        if a['approver'].status != "approved" and a['approver'].id != approver.id:
                            _logger.info("first_1")
                            create_request = False
                            break;
                        elif a['approver'].status == "approved" and a['approver'].id != approver.id:
                            _logger.info("first_2")
                            pass;
                        elif a['approver'].user_id.x_studio_approve_payment_max < approver.request_id.amount:
                            _logger.info("first")
                            create_request = False
                            break;
                        elif a['approver'].status != "approved" and a['approver'].id == approver.id: 
                            _logger.info("second")
                            create_request=True
                            break;
                        # elif a.id == approver.id:
                        #     create_request=True
                        #     break;
                        elif a['approver'].status == 'approved':
                            _logger.info("third")
                            pass
                        else:
                            create_request=False
                            _logger.info("forth")
                            break;
            _logger.info(create_request)
            # updated to create under the vendor payments
            # Check if a payment request should be created
            if create_request == True:
                # Search for the oldest "bank" type journal
                journal = self.env['account.journal'].search(
                    [('type', "=", "bank")], order="create_date asc", limit=1)
                
                # Get the manual outbound payment method
                payment_method = self.env.ref('account.account_payment_method_manual_out')
                
                # Prepare the values for the new payment
                val = {
                    "payment_type": "outbound",  # The payment is outbound (we are paying a vendor)
                    "partner_type": "supplier",  # The partner is a supplier
                    "partner_id": approver.request_id.partner_id.id,  # The partner's ID
                    "amount": approver.request_id.amount,  # The amount of the payment
                    "date": approver.request_id.date,  # The date of the payment
                    "journal_id": journal.id,  # The journal where the payment will be recorded
                    "payment_method_id": payment_method.id,
                    "ref":approver.request_id.name
                  # The payment method
                }
                
                # Log the prepared values
                _logger.info(val)
                
                # Create the new payment
                result = self.env['account.payment'].create(val)
                
                # Link the new payment to the approval request
                approver.request_id.reciept_id = result.id
                
                # Log the created payment
                _logger.info(result)







            # # wsdgasdvh
            # if create_request == True:

            #         # _logger.info(a.user_id.	x_studio_approve_payment_max) 
            #         _logger.info("########################################")
                    
            #         # status_lst = approver.request_id.mapped('approver_ids.status')
            #         # minimal_approver = approver.request_id.approval_minimum if len(
            #         #     status_lst) >= approver.request_id.approval_minimum else len(status_lst)
            #         # _logger.info("begin cheking status 1")
            #         # status = ""
            #         # # sdsdefwefe
            #         # if status_lst:
            #         #     if status_lst.count('cancel'):
            #         #         status = 'cancel'
            #         #     elif status_lst.count('refused'):
            #         #         status = 'refused'
            #         #     elif status_lst.count('new'):
            #         #         status = 'new'
            #         #     elif status_lst.count('approved') >= minimal_approver:
            #         #         status = 'approved'
            #         #     # else:
            #         #     #     status = 'pending' 
            #         #     elif status_lst.count('approved') == minimal_approver - 1:
            #         #         status = 'pending'
            #         # _logger.info(status)
            #         # _logger.info(minimal_approver)
            #         # if status == 'pending':



            #         journal = self.env['account.journal'].search(
            #             [('type', "=", "bank")], order="create_date asc", limit=1)
            #         val = {
            #             # "partner_id": approver.request_id.partner_id.id,
            #             "journal_id": journal.id,
            #             "move_type": "in_invoice",
            #             "invoice_date": approver.request_id.date,
            #             "date": approver.request_id.date,
            #         }
            #         if approver.request_id.partner_id != False:
            #             val['partner_id'] = approver.request_id.partner_id.id
            #         if approver.request_id.reference != False:
            #             val['contact_name'] = approver.request_id.reference
            #         line_data = {
            #             "account_id": journal.default_account_id.id,
            #             "quantity": 1,
            #             "price_unit": approver.request_id.amount,
            #             "price_subtotal": approver.request_id.amount,
            #             "partner_id":  approver.request_id.partner_id.id,

            #         }
            #         _logger.info("finished invoice line")
            #         invoice_line = (0, 0, line_data)
            #         val['invoice_line_ids'] = [invoice_line]
            #         _logger.info(val)
            #         result = self.env['account.payment'].create(val)
            #         approver.request_id.reciept_id = result.id
            #         _logger.info(result)
        approver.write({'status': 'approved'})
        self.sudo()._get_user_approval_activities(user=self.env.user).action_feedback()
        # if approver.request_id.category_id.id == 1:
        #     status_lst = approver.request_id.mapped('approver_ids.status')
        #     minimal_approver = approver.request_id.approval_minimum if len(
        #         status_lst) >= approver.request_id.approval_minimum else len(status_lst)
        #     _logger.info("begin cheking status type 2")
        #     if status_lst:
        #         if status_lst.count('cancel'):
        #             status = 'cancel'
        #         elif status_lst.count('refused'):
        #             status = 'refused'
        #         elif status_lst.count('new'):
        #             status = 'new'
        #         elif status_lst.count('approved') >= minimal_approver:
        #             status = 'approved'
        #         else:
        #             status = 'pending'
        #     if status == 'pending':
        #         journal = self.env['account.journal'].search(
        #             [('type', "=", "purchase")], order="create_date asc", limit=1)
        #         val = {
        #             "partner_id": approver.request_id.partner_id.id,
        #             "date_order": approver.request_id.date,
        #             # "pricelist_id": "
        #         }
        #         product_line = []
        #         for each_line in approver.request_id.product_line_ids:
        #             line_data = {
        #                 "product_id": each_line.product_id.id,
        #                 "discount": each_line.discount,
        #                 "product_uom_qty": each_line.quantity,
        #             }
        #             _logger.info("Finished line data")
        #             invoice_line = (0, 0, line_data)
        #             product_line.append(invoice_line)
        #         val['order_line'] = product_line
        #         _logger.info(val)
        #         result = self.env['sale.order'].create(val)
        #         _logger.info(result)


class RecieptJournalEntry(models.Model):
    _inherit = "account.move"

    contact_name = fields.Char(string='Contact Name')
