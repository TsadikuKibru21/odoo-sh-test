
/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
// var models = require('point_of_sale.models');

patch(Order.prototype, {

// models.Order =  models.Order.extend({
        initialize: function(attr, options) {
            _super_order.initialize.call(this,attr,options);
            _super_order.initialize.apply(this, arguments);
            this.uiState = {
                ReceiptScreen: new Context({
                    inputEmail: '',
                    emailSuccessful: null,
                    emailNotice: '',
                }),
                TipScreen: new Context({
                    inputTipAmount: '',
                }),
                PaymentScreen: new Context({
                    inputPhoneNumber: '',
                }),
            };
        },


    });

// });