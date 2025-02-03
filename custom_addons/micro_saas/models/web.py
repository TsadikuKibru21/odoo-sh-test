from odoo import models, fields, api
import logging

# Initialize logger
_logger = logging.getLogger(__name__)
class WebsiteTemplate(models.Model):
    _inherit = 'website.page'

    name = fields.Char(string="Name")
    email = fields.Char(string="Email")

    def action_submit(self):
        # Add your logic here for what happens when the button is clicked
        # For example, you might want to send an email or log information
        # This is just a placeholder message
        _logger.info("############################## test come ######################################")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Submitted',
                'message': 'The form has been submitted successfully.',
                'type': 'success',
            }
        }
