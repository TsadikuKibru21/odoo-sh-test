# -*- coding: utf-8 -*-
# Copyright (C) 2023 Konos and MercadoPago S.A.
# Licensed under the GPL-3.0 License or later.
from odoo import http

import logging
import time
import hmac
import base64
import json
import hashlib
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)
import json

_logger = logging.getLogger(__name__)
class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'
    check_url = fields.Char('Payment Confirm URL')
    
    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('telebirr', 'Telebirr')]

    name = fields.Char(string="Payment Method", required=True, translate=True)
    receivable_account_id = fields.Many2one('account.account',
        string='Intermediary Account',
        required=True,
        domain=[('reconcile', '=', True), ('user_type_id.type', '=', 'receivable')],
        default=lambda self: self.env.company.account_default_pos_receivable_account_id,
        ondelete='restrict',
        help='Account used as counterpart of the income account in the accounting entry representing the pos sales.')
    is_cash_count = fields.Boolean(string='Cash')
    cash_journal_id = fields.Many2one('account.journal',
        string='Cash Journal',
        ondelete='restrict',
        help='The payment method is of type cash. A cash statement will be automatically generated.')
    split_transactions = fields.Boolean(
        string='Split Transactions',
        default=False,
        help='If ticked, each payment will generate a separated journal item. Ticking that option will slow the closing of the PoS.')
    open_session_ids = fields.Many2many('pos.session', string='Pos Sessions', compute='_compute_open_session_ids', help='Open PoS sessions that are using this payment method.')
    config_ids = fields.Many2many('pos.config', string='Point of Sale Configurations')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    use_payment_terminal = fields.Selection(selection=lambda self: self._get_payment_terminal_selection(), string='Use a Payment Terminal', help='Record payments with a terminal on this journal.')
    hide_use_payment_terminal = fields.Boolean(compute='_compute_hide_use_payment_terminal', help='Technical field which is used to '
                                               'hide use_payment_terminal when no payment interfaces are installed.')

    active = fields.Boolean(default=True)
    telebirr_api_key = fields.Char('API Key')
    telebirr_app_id = fields.Char('APP ID')
    telebirr_trace_no = fields.Char('Trace No')
    telebirr_payment = fields.Many2one('telebirr.payment', string='Telebirr payment')
    telebirr_url = fields.Char('URL')

    @api.onchange('use_payment_terminal')
    def onchange_payment_terminal_telebirr(self):
        if self.use_payment_terminal == 'telebirr':
            telebirr_pay = self.env['telebirr.payment'].search([], limit=1)
            if telebirr_pay:
                self.telebirr_payment = telebirr_pay.id
            else:
                tele_created = self.env['telebirr.payment'].create({
                    'name': 'Telebirr'
                })
                self.telebirr_payment = tele_created.id

    @api.depends('is_cash_count')
    def _compute_hide_use_payment_terminal(self):
        no_terminals = not bool(self._fields['use_payment_terminal'].selection(self))
        for payment_method in self:
            payment_method.hide_use_payment_terminal = no_terminals or payment_method.is_cash_count

    @api.onchange('use_payment_terminal')
    def _onchange_use_payment_terminal(self):
        """Used by inheriting model to unset the value of the field related to the unselected payment terminal."""
        pass

    @api.depends('config_ids')
    def _compute_open_session_ids(self):
        for payment_method in self:
            payment_method.open_session_ids = self.env['pos.session'].search([('config_id', 'in', payment_method.config_ids.ids), ('state', '!=', 'closed')])

    @api.onchange('is_cash_count')
    def _onchange_is_cash_count(self):
        if not self.is_cash_count:
            self.cash_journal_id = False
        else:
            self.use_payment_terminal = False

    def _is_write_forbidden(self, fields):
        return bool(fields and self.open_session_ids)

    def write(self, vals):
        if self._is_write_forbidden(set(vals.keys())):
            raise UserError('Please close and validate the following open PoS Sessions before modifying this payment method.\n'
                            'Open sessions: %s' % (' '.join(self.open_session_ids.mapped('name')),))
        return super(PosPaymentMethod, self).write(vals)
    # def find_pay_confirmed_telebirr(self, id):
    #     response =  {
    #                 'msg': 'Success'
    #                 }
    #     _logger.info("55555555554444444444444455555555")
    #     _logger.info(response)

    #     return response

    def find_pay_confirmed_telebirr(self, id):
        pos_ses = self.env['pos.config'].search([('id', '=', id)])
        # _logger.info("55555555554444444444444455555555")
        _logger.info(pos_ses.telebirr_payment.pay_confirmed)

        if pos_ses.telebirr_payment:
            _logger.info("Trueeeeee")


            if pos_ses.telebirr_payment.pay_confirmed == 'confirmed':
                _logger.info("Paiddddd")

                return {
                    'msg': 'Success'
                       }
            elif pos_ses.telebirr_payment.pay_confirmed == 'failed':
                return {
                    'msg': 'Failed'
                       }
        else:
            return {
                'msg': 'Failed'
                   }
    def send_request_telebirr(self, data):
        _logger.info(data)
        self.sudo().telebirr_payment.trace_no = ' '
        pay_config = self.env['pos.config'].sudo().search([('id', '=', data['pos_session'])])
        pay_search = self.env['telebirr.payment'].sudo().search([('id', '=', pay_config.telebirr_payment.id)])
        pay_online_search = self.env['pos.online.payment'].sudo().search([('name', '=', data['traceNo'])])
        if not pay_online_search:
            pay_online = self.env['pos.online.payment'].sudo().create({
                'name': data['traceNo'],
                'pay_method': 'Telebirr',
                'price': data['amount'],
                'payer_id': data['payerId'],
                'pos_config': pay_config.id
            })
        res = {
           'trace_no': data['traceNo'],
            'pay_confirmed': 'progress'
        }
        pay_search.sudo().write(res)
        data['apiKey'] = self.telebirr_api_key
        data['payerId']=data['payerId']
        # send_sms = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/send_sms'
        headers = {'Content-Type': 'application/json'}
        _logger.info("DATAAAAAAAAAAAAAAA")
        _logger.info(data)
        response = requests.post(self.telebirr_url, json=data, headers=headers)
        self.sudo().telebirr_payment.trace_no = data['traceNo']
        lod_json = json.loads(response.text)
        _logger.info("555555555555555555")
        _logger.info(lod_json['result'])

        print("LOAD JSOM")
        print(lod_json['result'])
        if lod_json['result'] == 'USSD Sent Successfully':
            msg = 'Success'
        else: msg = 'Failure'
        return {
                'response': lod_json['result'],
                'msg': msg,
                'trace_no': data['traceNo']
        }



























        # body = self._paytm_get_request_body(transaction_id, reference_id, timestamp)
    # def send_request_telebirr(self,data):
        # self.sudo().telebirr_payment.trace_no = ' '
        # pay_config = self.env['pos.config'].sudo().search([('id', '=', data['pos_session'])])
        # pay_search = self.env['telebirr.payment'].sudo().search([('id', '=', pay_config.telebirr_payment.id)])
        # pay_online_search = self.env['pos.online.payment'].sudo().search([('name', '=', data['traceNo'])])
        # if not pay_online_search:
        #     pay_online = self.env['pos.online.payment'].sudo().create({
        #         'name': data['traceNo'],
        #         'pay_method': 'Telebirr',
        #         'price': data['amount'],
        #         'payer_id': self.telebirr_app_id,
        #         'pos_config': pay_config.id
        #     })
        # res = {
        #    'trace_no': data['traceNo'],
        #     'pay_confirmed': 'progress'
        # }
        # pay_search.sudo().write(res)
        # data['apiKey'] = self.telebirr_api_key
        # send_sms = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/send_sms'
        # headers = {'Content-Type': 'application/json'}
        # _logger.info("DATAAAAAAAAAAAAAAA")
        # _logger.info(data)
        # response = requests.post(self.telebirr_url, json=data, headers=headers)
        # self.sudo().telebirr_payment.trace_no = data['traceNo']
        # lod_json = json.loads(response.text)
        # _logger.info("555555555555555555")
        # _logger.info(lod_json['result'])

        # print("LOAD JSOM")
        # print(lod_json['result'])
        # if lod_json['result'] == 'USSD Sent Successfully':
        #     msg = 'Success'
        # else: msg = 'Failure'

        # return {
        #         'response': lod_json['result'],
        #         'msg': msg,
        #         'trace_no': data['traceNo']
        # }


    # def send_request_trace_no(self, data):
    #     headers = {'Content-Type': 'application/json'}
    #     pay_meth = self.env['pos.payment.method'].search([('id', '=', data['payment_method'])])
    #     if pay_meth:
    #         response = requests.post('http://196.189.44.60:8069/telebirr/ussd/local_query', json=data, headers=headers)
    #         lod_json = json.loads(response.text)
    #         amount = round(data['amount'], 2)
    #         print(lod_json, 'JSON', amount)
    #         if lod_json['result'] == 'could not find':
    #             return {
    #                 'msg': 'failed',
    #                 'longMsg': 'Trace Number Not Found'
    #             }
    #         else:
    #             if lod_json['result']['msg'] == 'pending' and lod_json['result']['amount'] == amount:
    #                 return {
    #                     'msg': 'pending',
    #                     'longMsg': 'Transaction is not Completed',
    #                 }
    #             elif lod_json['result']['msg'] == 'confiremed' and lod_json['result']['amount'] == amount:
    #                 return {
    #                     'msg': 'Success',
    #                     'longMsg': 'Transaction is Completed',
    #                 }
    #             elif lod_json['result']['msg'] == 'failed' and lod_json['result']['amount'] == amount:
    #                 return {
    #                     'msg': 'failed',
    #                     'longMsg': 'Transaction has Failed',
    #                 }
    #             elif lod_json['result']['amount'] != amount:
    #                 return {
    #                     'msg': 'failed',
    #                     'longMsg': 'The price is incorrect',
    #                 }

    #     else:
    #         return {
    #             'longMsg': 'No Payment Method Found'
    #     }

















# MAX_RETRIES = 40
# MIN_SALE = 50.0
# TIMEOUT = 10

# BASE_URL = {
#     "live": "https://api.redelcom.cl:20010",
#     "demo": "https://api-dev.redelcom.cl:20010",
# }


# class PosPaymentMethod(models.Model):
#     _inherit = "pos.payment.method"

#     redelcom_mode = fields.Selection([
#         ("live", "Live"),
#         ("demo", "Demo")],
#         default="demo", copy=False,
#         help="Environment in which transactions are executed.")
#     redelcom_client = fields.Integer(
#         copy=False,
#         help="Client identifier in the Redelcom system.")
#     redelcom_secret = fields.Char(
#         copy=False,
#         help="Secret key assigned to the client.")
#     redelcom_terminal_serial = fields.Char(
#         copy=False,
#         help="10-digit number located on the back of the terminal.")
#     redelcom_terminal_code = fields.Char(
#         copy=False,
#         help="Unique identifier associated with the terminal.")

#     def _get_payment_terminal_selection(self):
#         """
#         Enables 'Redelcom' as a payment terminal for payment methods.

#         :return: Payment terminals available.
#         :rtype: list
#         """
#         res = super()._get_payment_terminal_selection()
#         res.append(["redelcom", "Redelcom"])
#         return res

#     def _redelcom_authentication_token(self, endpoint, data):
#         """
#         Generates the authentication token for Redelcom API requests.

#         :param endpoint: URL for which you want to make the request (str).
#         :param data: Data to be included as part of the request (dict).

#         :return: A string representing the authentication token.
#         :rtype: str

#         :raises UserError: If there is an error generating the token.
#         """
#         # try:
#         #     message = f"{endpoint},{data}"
#         #     hmac_object = hmac.new(
#         #         bytes(self.redelcom_secret, "utf-8"),
#         #         msg=bytes(message, "utf-8"),
#         #         digestmod=hashlib.sha256).digest()
#         #     hmac_encode = base64.b64encode(hmac_object)
#         #     token = f"{self.redelcom_client};{hmac_encode.decode('UTF-8')}"
#         # except Exception as error:
#         #     _logger.exception("_redelcom_authentication_token: %s", error)
#         #     raise UserError(_("Unable to generate authentication token"))
#         # return token

#     @api.model
#     def _redelcom_get_terminal_code(self, serial, mode):
#         """
#         Retrieves the unique identifier associated with the terminal.

#         :param serial: The serial number of the terminal (str).
#         :param mode: The mode of API request (str).

#         :return: The response object containing the terminal identifier.
#         :rtype: requests.models.Response

#         :raises UserError: If there is an error retrieving the identifier.
#         """
        

#         # try:
#         #     endpoint = f"/v2/terminal?serialNumber={serial}"
#         #     headers = {
#         #         "X-Authentication":
#         #             self._redelcom_authentication_token(endpoint, "")
#         #     }
#         #     url = "".join([BASE_URL.get(mode), endpoint])
#         #     response = requests.get(url, headers=headers, timeout=TIMEOUT)
#         #     response.raise_for_status()
#         # except requests.exceptions.RequestException as error:
#         #     _logger.exception("_redelcom_get_terminal_code: %s", error)
#         #     raise UserError(_("Unable to retrieve the terminal code"))
#         # return response

#     def _redelcom_create_payment_intent(self, pos_ref, name, amount):
#         """
#         Creates a payment intent in Redelcom.

#         :param pos_ref: The reference of the point of sale transaction (str).
#         :param name: The name or description of the payment (str).
#         :param amount: The amount of the payment (int).

#         :return: The response object containing the payment intent.
#         :rtype: requests.models.Response

#         :raises UserError: If there is an error creating the payment intent.
#         """
#         # try:
#         #     endpoint = "/v2/pago"
#         #     payload = json.dumps({
#         #         "userTransactionId": pos_ref,
#         #         "description": name,
#         #         "amount": amount,
#         #         "terminalId": self.redelcom_terminal_code,
#         #         # Although you can pay with card, cash or wallet, we
#         #         # will always use card by default.
#         #         "paymentType": "TARJETA",
#         #     })
#         #     headers = {
#         #         "X-Authentication":
#         #             self._redelcom_authentication_token(endpoint, payload),
#         #         "Content-Type": "application/json"
#         #     }
#         #     url = "".join([BASE_URL.get(self.redelcom_mode), endpoint])
#         #     response = requests.post(
#         #         url, headers=headers, data=payload, timeout=TIMEOUT)
#         #     response.raise_for_status()
#         # except requests.exceptions.RequestException as error:
#         #     _logger.exception("_redelcom_create_payment_intent: %s", error)
#         #     raise UserError(_("Unable to create payment intent"))
#         # return response

#     def _redelcom_get_payment_status(self, transaction_id):
#         """
#         Retrieves the payment status of the transaction from Redelcom.

#         :param transaction_id: ID used to identify the payment (str).

#         :return: The response object containing the payment status.
#         :rtype: requests.models.Response

#         :raises UserError: If there is an error retrieving the payment status.
#         """
#         # try:
#         #     endpoint = f"/v2/pago?rdcTransactionId={transaction_id}"
#         #     headers = {
#         #         "X-Authentication":
#         #             self._redelcom_authentication_token(endpoint, "")
#         #     }
#         #     url = "".join([BASE_URL.get(self.redelcom_mode), endpoint])
#         #     response = requests.get(url, headers=headers, timeout=TIMEOUT)
#         #     response.raise_for_status()
#         # except requests.exceptions.RequestException as error:
#         #     _logger.exception("_redelcom_get_payment_status: %s", error)
#         #     raise UserError(_("Unable to retrieve payment status"))
#         # return response

#     def redelcom_make_payment(self, pos_ref, name, amount):
#         """
#         Initiates a payment transaction through Redelcom API.

#         :param pos_ref: The reference of the point of sale transaction (str).
#         :param name: The name or description of the payment (str).
#         :param amount: The amount of the payment (int).

#         :return: Details of the transaction.
#         :rtype: dict

#         :raises ValidationError: If there are validation errors preventing
#             the payment.
#         :raises UserError: If the transaction cannot be completed within
#             the maximum retries.
#         """
#         # conditions = {
#         #     _("The terminal code is not defined"):
#         #     not self.redelcom_terminal_code,
#         #     _("The sale amount does not reach the minimum required"):
#         #     amount <= MIN_SALE,
#         # }
#         # messages = [key for key, value in conditions.items() if value]
#         # if messages:
#         #     raise ValidationError(_(
#         #         "Cannot continue due to the following:\n%s") %
#         #             ("\n".join(messages)))
#         # _logger.info("Creating payment intention")
#         # intent_request = self._redelcom_create_payment_intent(
#         #     pos_ref, name, amount)
#         # intent = intent_request.json()
#         # transaction_id = intent.get("rdcTransactionId")
#         # data = {}
#         # retries = MAX_RETRIES
#         # # We keep making requests until we get a response or reach
#         # # the maximum number of retries. In the worst case we wait
#         # # 160 seconds before aborting the transaction
#         # _logger.info("Getting payment status")
#         # while retries > 0:
#         #     _logger.info("Remaining attempts: %s", retries)
#         #     time.sleep(4)
#         #     payment_request = self._redelcom_get_payment_status(
#         #         transaction_id)
#         #     if payment_request.status_code == 204:
#         #         retries -= 1
#         #         continue
#         #     payment = payment_request.json()
#         #     if payment.get("ESTADO") in ["APROBADO", "RECHAZADO"]:
#         #         data.update({
#         #             "state": payment.get("ESTADO"),
#         #             "message": payment.get("MENSAJE_VISOR"),
#         #             "transaction_id": transaction_id,
#         #             "card_type": payment.get("MEDIO_PAGO"),
#         #         })
#         #         break
#         #     retries -= 1
#         # if not data:
#         #     raise UserError(_(
#         #         "Transaction %s could not be completed") % transaction_id)
#         # return data

#     @api.model_create_multi
#     def create(self, vals_list):
#         records = super().create(vals_list)
#         for record in records:
#              terminal = record.use_payment_terminal
#             # if terminal and terminal == "redelcom":
#         # code_request = record._redelcom_get_terminal_code(
#         # record.redelcom_terminal_serial,record.redelcom_mode)
#                 # code = code_request.json()
#              record.write({
#                     "redelcom_terminal_code": "123456"})
#         return records

#     def write(self, vals):
#         # if "redelcom_terminal_serial" in vals and\
#             # self.use_payment_terminal == "redelcom":
#             serial = "123456"
#             # mode = self.redelcom_mode
#             # code_request = self._redelcom_get_terminal_code(serial, mode)
#             # code = code_request.json()
#             vals.update({ "redelcom_terminal_code": "123456"})
#             return super().write(vals)




#     # @api.model_create_multi
#     # def create(self, vals_list):
#     #     records = super().create(vals_list)
#     #     for record in records:
#     #         terminal = record.use_payment_terminal
#     #         if terminal and terminal == "redelcom":
#     #             code_request = record._redelcom_get_terminal_code(
#     #                 record.redelcom_terminal_serial,
#     #                 record.redelcom_mode)
#     #             code = code_request.json()
#     #             record.write({
#     #                 "redelcom_terminal_code": code.get("terminal")})
#     #     return records

#     # def write(self, vals):
#     #     if "redelcom_terminal_serial" in vals and\
#     #             self.use_payment_terminal == "redelcom":
#     #         serial = vals.get("redelcom_terminal_serial")
#     #         mode = self.redelcom_mode
#     #         code_request = self._redelcom_get_terminal_code(serial, mode)
#     #         code = code_request.json()
#     #         vals.update({
#     #             "redelcom_terminal_code": code.get("terminal")})
#     #     return super().write(vals)
