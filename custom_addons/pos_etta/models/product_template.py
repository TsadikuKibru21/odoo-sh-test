from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_charge = fields.Float(string='Service Charge')
    # default_code = fields.Char(
    #     'Internal Reference', compute='_compute_default_code',
    #     inverse='_set_default_code', store=True, required=True)
    
    @api.constrains('taxes_id')
    def _check_taxes_id(self):
        for record in self:
            if len(record.taxes_id) > 1:
                raise ValidationError(_("You can only select one tax per product."))