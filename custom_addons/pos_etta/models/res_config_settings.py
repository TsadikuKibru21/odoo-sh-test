from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    disable_remove_order_line_basic_right = fields.Boolean(related='pos_config_id.disable_remove_order_line_basic_right', readonly=False)
    global_service_charge =  fields.Float(related='pos_config_id.global_service_charge', readonly=False)
    pos_module_pos_service_charge = fields.Boolean(related='pos_config_id.pos_module_pos_service_charge', readonly=False)
    serial_number = fields.Char(related='pos_config_id.serial_number',readonly=False)
    fiscal_mrc = fields.Char(related='pos_config_id.fiscal_mrc',readonly=False)
    pos_customer_id = fields.Many2one('res.partner', related='pos_config_id.pos_customer_id', readonly=False)
    
    enabled_zmall = fields.Boolean(related='pos_config_id.enabled_zmall', readonly=False)
    zmall_api_endpoint = fields.Char(related='pos_config_id.zmall_api_endpoint', readonly=False)
    zmall_username = fields.Char(related='pos_config_id.zmall_username', readonly=False)
    zmall_password = fields.Char(related='pos_config_id.zmall_password', readonly=False)


    # @api.onchange('enabled_zmall', 'zmall_api_endpoint', 'zmall_username', 'zmall_password')
    # def _onchange_zmall_fields(self):
    #     if self.enabled_zmall and self.zmall_api_endpoint and self.zmall_username and self.zmall_password:
    #         _logger.info("************************************************************************************")
    #         self.auth_zmall()

    # @api.model
    # def auth_zmall(self):
    #     headers = {'Content-Type': 'application/json'}
    #     # pos_config = self.env['pos.config'].search([('id','=', data)], limit=1)
    #     request_data = {"email": self.zmall_username, "password": self.zmall_password}        
    #     auth_endpoint = self.zmall_api_endpoint + 'api/store/login'
    #     _logger.info("****************************************************")
    #     _logger.info("**********************************************************")
    #     _logger.info("********************************************************")

    #     try:
    #         response = requests.post(str(auth_endpoint), json=request_data, headers=headers)
    #         _logger.info("**************************************response********************")
    #         _logger.info(response.text)
    #     except:
    #         return {
    #             'msg': 'Failed',
    #             'longMsg': "Couldn't connect with Zmall"
    #         }

    #     response_json = json.loads(response.text)
    #     # return str(response_json['success'])
    #     if str(response_json['success']) == 'True':
    #         return {
    #             'server_token': response_json['store']['server_token'], 
    #             'store_id': response_json['store']['_id']
    #         }
    #     elif str(response_json['success']) == 'False':
    #         return {
    #             'error_code': response_json['store']['server_token']
    #         }
    #     else:
    #         return {
    #             'error': 'Unknown Error'
    #         }
    #     # return response_json

    # def get_zmall_orders(self, req):
    #     headers = {'Content-Type': 'application/json'}
    #     pos_config = self.env['pos.config'].search([('id','=', req['config_id'])], limit=1)
    #     request_data = {
    #         "store_id": req['store_id'],
    #         "server_token": req['server_token'],
    #         "payment_mode": "",
    #         "order_type": "",
    #         "pickup_type": "",
    #         "search_field": "user_detail.first_name",
    #         "search_value": "",
    #         "page": 1
    #     }
    #     get_orders_endpoint = pos_config.zmall_api_endpoint + 'api/store/order_list_search_sort'

    #     try:
    #         response = requests.post(str(get_orders_endpoint), json=request_data, headers=headers)
    #     except:
    #         return {
    #             'msg': 'Failed',
    #             'longMsg': "Couldn't connect with Zmall"
    #         }

    #     response_json = json.loads(response.text)
    #     if str(response_json['success']) == 'True':
    #         orders_response = []
    #         for order in response_json['orders']:
    #             zmall_order_id = order['_id']
    #             store_id = order['store_id']
    #             unique_id = order['unique_id']
    #             created_at = order['created_at']
    #             order_status = order['order_status']
    #             customer_name = order['user_detail']['first_name']
    #             total_cart_price = order['cart_detail']['total_cart_price']
    #             cart_items = []

    #             for cart in order['cart_detail']['order_details']:
    #                 # cart_id = new_zmall_order_data.id
    #                 category_name = cart['product_name']
    #                 for item in cart['items']:
    #                     item_unique_id = item['unique_id']
    #                     note_for_item = item['note_for_item']
    #                     full_product_name = item['item_name']
    #                     total_item_price = item['total_item_price']

    #                 cart_items.append({
    #                     # 'cart_id': cart_id,
    #                     'category_name': category_name,
    #                     'unique_id': item_unique_id,
    #                     'full_product_name': full_product_name,
    #                     'note_for_item': note_for_item,
    #                     'total_item_price': total_item_price,
    #                 })

    #             orders_response.append({
    #                 'zmall_order_id': zmall_order_id,
    #                 'store_id': store_id,
    #                 'unique_id': unique_id,
    #                 'created_at': created_at,
    #                 'order_status': order_status,
    #                 'customer_name': customer_name,
    #                 'total_cart_price': total_cart_price,
    #                 'cart_items': cart_items
    #             })

    #         return orders_response




    #             # existing_order = self.env['pos.zmall.order'].search([('zmall_order_id','=', zmall_order_id)])

    #             # if not existing_order:
    #                 # new_zmall_order_data = self.env['pos.zmall.order'].sudo().create({
    #                 #     'zmall_order_id': zmall_order_id,
    #                 #     'unique_id': unique_id,
    #                 #     'created_at': created_at,
    #                 #     'order_status': order_status,
    #                 #     'customer_name': customer_name,
    #                 #     'total_cart_price': total_cart_price,
    #                 # })

    #             #     for cart in order['cart_detail']['order_details']:
    #             #         cart_id = new_zmall_order_data.id
    #             #         category_name = order['product_name']
    #             #         for item in cart['items']:
    #             #             item_unique_id = item['unique_id']
    #             #             note_for_item = item['note_for_item']
    #             #             full_product_name = item['item_name']
    #             #             total_item_price = item['total_item_price']

    #                     # new_zmall_order_line_data = self.env['pos.zmall.order.line'].sudo().create({
    #                     #     'cart_id': cart_id,
    #                     #     'category_name': category_name,
    #                     #     'unique_id': item_unique_id,
    #                     #     'full_product_name': full_product_name,
    #                     #     'note_for_item': note_for_item,
    #                     #     'total_item_price': total_item_price,
    #                     # })
    #     else:
    #         return response_json

    # def set_zmall_order_status(self, req):
    #     _logger.info("==================== >>>>>>>>> req config id")
    #     _logger.info(req)
    #     _logger.info("==================== >>>>>>>>> req config id")
    #     headers = {'Content-Type': 'application/json'}
    #     pos_config = self.env['pos.config'].search([('id','=', req['config_id'])], limit=1)
    #     request_data = {
    #         "store_id": req['store_id'],
    #         "server_token": req['server_token'],
    #         "order_status": req['order_status'],
    #         "order_id": req['order_id']
    #     }
    #     get_orders_endpoint = pos_config.zmall_api_endpoint + 'api/store/set_order_status'

    #     try:
    #         response = requests.post(str(get_orders_endpoint), json=request_data, headers=headers)
    #     except:
    #         return {
    #             'msg': 'Failed',
    #             'longMsg': "Couldn't connect with Zmall"
    #         }

    #     response_json = json.loads(response.text)
    #     if str(response_json['success']) == 'True':
    #         return 'done'
    #     else:
    #         if response_json['error_code'] == 999:
    #             return 'reauth'
    #         return 'error'

    # def get_store_info(self, req):
    #     headers = {'Content-Type': 'application/json'}
    #     pos_config = self.env['pos.config'].search([('id','=', req['config_id'])], limit=1)
    #     request_data = {
    #         "store_id": req['store_id'],
    #         "server_token": req['server_token'],
    #         "type": 2
    #     }
    #     get_orders_endpoint = pos_config.zmall_api_endpoint + 'api/store/get_store_data'

    #     try:
    #         response = requests.post(str(get_orders_endpoint), json=request_data, headers=headers)
    #     except:
    #         return {
    #             'msg': 'Failed',
    #             'longMsg': "Couldn't connect with Zmall"
    #         }

    #     response_json = json.loads(response.text)
    #     _logger.info("================== storedata adsfgfhgfdsadfggdwsfdgsfe")
    #     _logger.info(response_json)
    #     if str(response_json['success']) == 'True':
    #         storedata = {
    #             'store_name': response_json['store_detail']['name'],
    #             'is_visible': response_json['store_detail']['is_visible'],
    #             'is_business': response_json['store_detail']['is_business'],
    #             'admin_profit_value_on_delivery': response_json['store_detail']['city_details']['admin_profit_value_on_delivery'],
    #             'is_store_busy': response_json['store_detail']['is_store_busy'],
    #             'accept_only_cashless_payment': response_json['store_detail']['accept_only_cashless_payment'],
    #             'accept_scheduled_order_only': response_json['store_detail']['accept_scheduled_order_only']
    #         }
    #         return storedata
    #     else:
    #         if response_json['error_code'] == 999:
    #             return 'reauth'
    #         return 'error'

    # def set_store_info(self, req):
    #     headers = {'Content-Type': 'application/json'}
    #     pos_config = self.env['pos.config'].search([('id','=', req['config_id'])], limit=1)
    #     request_data = {
    #         "store_id": req['store_id'],
    #         "server_token": req['server_token'],
    #         "order_status": req['order_status'],
    #         "order_id": req['order_id']
    #     }
    #     get_orders_endpoint = pos_config.zmall_api_endpoint + 'api/store/set_order_status'

    #     try:
    #         response = requests.post(str(get_orders_endpoint), json=request_data, headers=headers)
    #     except:
    #         return {
    #             'msg': 'Failed',
    #             'longMsg': "Couldn't connect with Zmall"
    #         }

    #     response_json = json.loads(response.text)
    #     if str(response_json['success']) == 'True':
    #         return 'done'
    #     else:
    #         if response_json['error_code'] == 999:
    #             return 'reauth'
    #         return 'error'

    # def get_zmall_products(self, req):
        # headers = {'Content-Type': 'application/json'}
        # pos_config = self.env['pos.config'].search([('id','=', req['config_id'])], limit=1)
        # request_data = {
        #     "store_id": req['store_id'],
        #     "server_token": req['server_token'],
        #     "type": 2
        # }
        # get_zmall_products_endpoint = pos_config.zmall_api_endpoint + 'api/store/get_item_list'

        # try:
        #     response = requests.post(str(get_zmall_products_endpoint), json=request_data, headers=headers)
        # except:
        #     return {
        #         'msg': 'Failed',
        #         'longMsg': "Couldn't connect with Zmall"
        #     }

        # response_json = json.loads(response.text)

        # if str(response_json['success']) == 'True':
        #     products_list = []
        #     for item in response_json['items']:
        #         item_id = item['_id']
        #         unique_id = item['unique_id']
        #         name = item['name']
        #         price = item['price']
        #         image_url = item['image_url']
        #         is_visible_in_store = item['is_visible_in_store']
        #         category_name = item['products_detail']['name']
        #         category_id = item['product_id']

        #         products_list.append({
        #             'item_id': item_id,
        #             'unique_id': unique_id,
        #             'name': name,
        #             'price': price,
        #             'image_url': image_url,
        #             'category_name': category_name,
        #             'category_id': category_id,
        #             'is_visible_in_store': is_visible_in_store
        #         })

        #     return products_list
        # else:
        #     return response_json