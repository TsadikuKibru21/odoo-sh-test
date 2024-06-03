# -*- coding: utf-8 -*-

from odoo import fields, models,tools,api
import json

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    table_id = fields.Many2one('restaurant.table', string='Table')
class pos_config(models.Model):
    _inherit = 'restaurant.table'
    # waiter_ids = fields.One2many('hr.employee', 'table_id', string='Waiters')
    waiter_ids = fields.Many2many('hr.employee', string='Waiters')


























