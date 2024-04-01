from odoo import fields, models, api, _
import logging
import requests
from odoo.http import request
_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'
    telebirr_payment = fields.Many2one('telebirr.payment', string='Telebirr payment')

    @api.model
    def create(self, values):
        IrSequence = self.env['ir.sequence'].sudo()
        tele_pay = self.env['telebirr.payment'].sudo().create({
            'name': 'Telebirr Payment',
            'pay_confirmed': 'new',
        })
        val = {
            'name': _('POS Order %s', values['name']),
            'padding': 4,
            'prefix': "%s/" % values['name'],
            'code': "pos.order",
            'company_id': values.get('company_id', False),
        }
        # force sequence_id field to new pos.order sequence
        values['sequence_id'] = IrSequence.create(val).id

        val.update(name=_('POS order line %s', values['name']), code='pos.order.line')
        values['sequence_line_id'] = IrSequence.create(val).id
        values['telebirr_payment'] = tele_pay.id
        pos_config = super(PosConfig, self).create(values)
        pos_config.sudo()._check_modules_to_install()
        pos_config.sudo()._check_groups_implied()

        # If you plan to add something after this, use a new environment. The one above is no longer valid after the modules install.
        return pos_config