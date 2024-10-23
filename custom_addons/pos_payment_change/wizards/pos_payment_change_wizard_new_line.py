# # Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# # @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# from odoo import api, fields, models


# class PosPaymentChangeWizardLine(models.TransientModel):
#     _name = "pos.payment.change.wizard.new.line"
#     _description = "PoS Payment Change Wizard New Line"

#     wizard_id = fields.Many2one(
#         comodel_name="pos.payment.change.wizard",
#         required=True,
#         ondelete="cascade",
#     )

#     new_payment_method_id = fields.Many2one(
#         comodel_name="pos.payment.method",
#         string="Payment Method",
#         required=True,
#         domain=lambda s: s.domain_new_payment_method_id(),
#     )

#     company_currency_id = fields.Many2one(
#         comodel_name="res.currency",
#         store=True,
#         related="new_payment_method_id.company_id.currency_id",
#         string="Company Currency",
#         readonly=True,
#         help="Utility field to express amount currency",
#     )

#     amount = fields.Monetary(
#         required=True,
#         default=0.0,
#         currency_field="company_currency_id",
#     )

#     @api.model
#     def domain_new_payment_method_id(self):
#         PosOrder = self.env["pos.order"]
#         order = PosOrder.browse(self.env.context.get("active_id"))
#         return [("id", "in", order.mapped("session_id.payment_method_ids").ids)]

#     # View Section
#     @api.model
#     def default_get(self, fields):
#         res = super().default_get(fields)
#         if "new_line_ids" not in self._context:
#             return res
#         balance = self._context.get("amount_total", 0.0)
#         for line in self.wizard_id.old_line_ids:
#             balance -= line.get("amount")
#         res.update({"amount": balance})
#         return res


from odoo import api, fields, models, _

class PosPaymentChangeWizardLine(models.TransientModel):
    _name = "pos.payment.change.wizard.new.line"
    _description = "PoS Payment Change Wizard New Line"

    wizard_id = fields.Many2one(
        comodel_name="pos.payment.change.wizard",
        required=True,
        ondelete="cascade",
    )

    new_payment_method_id = fields.Many2one(
        comodel_name="pos.payment.method",
        string="Payment Method",
        required=True,
        domain="[('id', 'in', payment_method_domain)]",  # Use a related field in the domain
    )

    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        store=True,
        related="new_payment_method_id.company_id.currency_id",
        string="Company Currency",
        readonly=True,
        help="Utility field to express amount currency",
    )

    amount = fields.Monetary(
        required=True,
        default=0.0,
        currency_field="company_currency_id",
    )

    payment_method_domain = fields.Many2many(
        comodel_name='pos.payment.method',
        compute='_compute_payment_method_domain',
        string="Available Payment Methods",
        help="Dynamically computed domain for the payment method"
    )

    @api.depends('wizard_id')
    def _compute_payment_method_domain(self):
        """
        Compute the available payment methods based on the current POS session of the order
        """
        for wizard_line in self:
            order = self.env['pos.order'].browse(self.env.context.get('active_id'))
            if order:
                wizard_line.payment_method_domain = order.session_id.payment_method_ids
            else:
                wizard_line.payment_method_domain = self.env['pos.payment.method']

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if "new_line_ids" not in self._context:
            return res
        balance = self._context.get("amount_total", 0.0)
        for line in self.wizard_id.old_line_ids:
            balance -= line.get("amount")
        res.update({"amount": balance})
        return res