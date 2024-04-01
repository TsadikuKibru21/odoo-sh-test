/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import {usePos} from "@point_of_sale/app/store/pos_hook";
// import { useListener } from "@web.custom_hooks"

patch(PaymentScreen.prototype, {
setup() {
    super.setup(...arguments);
        this.pos = usePos();
        console.log("LOADED PAYMENT SCREN",this.pos);
    },
        
  
    
    // _telebirr_pay: function () {
    //     console.log('_telebirr_pay', 'THIS', this.pos.get_order())
    //     var self = this;
    //     var order = this.pos.get_order();

    //     if (order.selected_paymentline.amount < 0) {
    //         this._show_error(_t('Cannot process transactions with negative amount.'));
    //         return Promise.resolve();
    //     }

    //     var uid = order.uid.replace(/-/g, '')
    //     var config = this.pos.config;
    //     console.log(order.uiState.PaymentScreen.state.inputPhoneNumber, uid, order.pos.user.company_id[1], 'COMPAYB')
    //     var random_val = Math.floor(Math.random() * 10000);
    //     var trace_no = random_val.toString().concat("_", uid);
    //     console.log(trace_no, 'TRAVVVE', this.pos.pos_session.config_id[0])

    //     var data = {
    //         "payerId": this.payment_method.telebirr_app_id,
    //         "pos_session": this.pos.pos_session.config_id[0],
    //         "traceNo": trace_no,
    //         "amount": order.selected_paymentline.amount,
    //         "phone": order.uiState.PaymentScreen.state.inputPhoneNumber
    //     }
    //     return this._call_telebirr(data).then(function (data) {
    //         return self._telebirr_handle_response(data);
    //     });
    // },

    // _call_telebirr: function (data, operation) {
    //     return jsonrpc({
    //         model: 'pos.payment.method',
    //         method: 'send_request_telebirr',
    //         args: [[this.payment_method.id], data],
    //     }, {
    //         // wait 10 seconds
    //         timeout: 10000,
    //         shadow: true,
    //     }).catch(this._handle_odoo_connection_failure.bind(this));
    // },
    



    // _telebirr_handle_response: function (response) {
    //     var line = this.pos.get_order().selected_paymentline;

    //     console.log('_telebirr_handle_response', this.pos.get_order(), 'UIO', this.pos.pos_session.config_id[0])

    //     if (response.status_code == 401) {
    //         this._show_error(_t('Authentication failed. Please check your Telebirr credentials.'));
    //         line.set_payment_status('force_done');
    //         return Promise.resolve();
    //     }

    //     if (response.msg && response.msg !== 'Success') {
    //         console.error('error from Telebirr', response.msg);

    //         var msg = '';

    //         this._show_error(_.str.sprintf(_t('An unexpected error occured. Message from Telebirr: %s'), response.response));
    //         if (line) {
    //             line.set_payment_status('force_done');
    //         }

    //         return Promise.resolve();
    //     } else {
    //         line.set_payment_status('waitingCard');

    //         var self = this;
    //         var res = new Promise(function (resolve, reject) {
    //             // clear previous intervals just in case, otherwise
    //             // it'll run forever
    //             clearTimeout(self.polling);

    //             self.polling = setInterval(function () {
    //                 self._poll_for_response(resolve, reject);
    //             }, 3000);
    //         });

    //         // make sure to stop polling when we're done
    //         res.finally(function () {
    //             self._reset_state();
    //         });

    //         return res;
    //     }
    // },



    }
);