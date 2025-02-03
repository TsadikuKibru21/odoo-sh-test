from odoo import http
from odoo.http import request
import logging

# Initialize logger
_logger = logging.getLogger(__name__)

class WebsiteFormController(http.Controller):

    @http.route('/form/submit', type='http', auth="public", website=True, methods=['GET'],csrf=False)
    def form_submit(self, **post):
        # Log the form data
        _logger.info("Form Data Received: %s", post)

        # Access individual form fields
        name = post.get('name')
        email = post.get('email')

        # Log the individual values for debugging purposes
        _logger.info("Name: %s, Email: %s", name, email)

        # Optionally, you can save this data to a model or send an email

        # Return a success message (this can be replaced with a redirect or a thank-you page)
        # return request.render('website.thank_you', {})


        # Redirect after form submission
    #     return request.redirect('/thank-you')

    # @http.route('/thank-you', type='http', auth="public", website=True)
    # def thank_you(self):
    #     return request.render('m.thank_you_template')
