from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'
    allow_waiter_reservation = fields.Boolean(
        string="Allow waiter table reservation",
    )
