from odoo import models

class PosSession(models.Model):
    """Model inherited to add additional functionality"""
    _inherit = 'pos.session'
    # def _loader_params_restaurant_table(self):
        # return {
        #     'search_params': {
        #         'domain': [('active', '=', True)],
        #         'fields': [
        #             'name', 'width', 'height', 'position_h', 'position_v',
        #             'shape', 'floor_id', 'color', 'seats', 'active'
        #         ],
        #     },
        
        # }
    def _loader_params_restaurant_table(self):
        res = super()._loader_params_restaurant_table()
        add_list = ["waiter_ids"]
        res['search_params']['fields'].extend(add_list)
        return res

#     def _pos_ui_models_to_load(self):
#         """Used to super the _pos_ui_models_to_load"""
#         result = super()._pos_ui_models_to_load()
#         result += [
#             'hr.employee'
#         ]
#         return result

#     def _loader_params_employee(self):
#         """Used to override the default settings for loading fields"""
#         return {
#             'search_params': {
#                 'fields': ['name'],
#             },
#         }

#     def _get_pos_ui_emloyee(self, params):
#         """Used to get the parameters"""
#         return self.env['hr.employee'].search_read(
#             **params['search_params'])