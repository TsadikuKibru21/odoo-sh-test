from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    allow_waiter_reservation = fields.Boolean(related='pos_config_id.allow_waiter_reservation', readonly=False)
