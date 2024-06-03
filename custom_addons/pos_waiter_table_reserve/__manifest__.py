# -*- coding: utf-8 -*-

{
    'name': 'Pos Waiter Table ReservationP',

    "version": "17.0.0.1",
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'ErpMstar Solutions',
    'summary': 'Allows waiter to reserve the table so other waiter will not allow to work on It.',
    'description': "Allows waiter to reserve the table so other waiter will not allow to work on It.",
    'depends': ['pos_restaurant'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_config_settings_views.xml'
    ],
    'assets': {
         'point_of_sale._assets_pos': [
            'pos_waiter_table_reserve/static/src/app/**/*',
            'pos_waiter_table_reserve/static/src/js/*',
            # 'pos_waiter_table_reserve/static/src/js/app/floor*',


        ],
        
        'web.assets_qweb': [
            'pos_waiter_table_reserve/static/src/xml/**/*',
        ],
    },
    'images': [
        'static/description/pos.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 99,
    'currency': 'EUR',
}
