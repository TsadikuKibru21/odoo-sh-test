// /** @odoo-module */
// console.log("LLLLLLLLLLLL")
// import { Payment } from "@point_of_sale/app/store/models";
// import { patch } from "@web/core/utils/patch";
// import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
// import { jsonrpc } from "@web/core/network/rpc_service";

// // patch(Payment.prototype, {


// export class PaymentTelebirr extends PaymentInterface {
// //   async  _telebirr_pay () {
// //         console.log('_telebirr_pay', 'THIS', this.pos.get_order().booked)
// //         var self = this;
// //         var order = this.pos.get_order();
// //         if (order.selected_paymentline.amount < 0) {
// //             this._show_error(_t('Cannot process transactions with negative amount.'));
// //             return Promise.resolve();
// //         }
// //         console.log("{{{{{{{{{{{")
// //         var uid = order.uid.replace(/-/g, '')
// //         console.log(uid)
// //         var config = this.pos.config;
// //         var random_val = Math.floor(Math.random() * 10000);
// //         console.log("@@@@@@@@@@@@22")
// //         console.log(order.uiState)
// //         var trace_no = random_val.toString().concat("_", uid);
// //         // console.log(trace_no, 'TRAVVVE', this.pos.pos_session.config_id[0])
// //         console.log(trace_no,"PPPPPPPP")
// //         var data = {
// //             "payerId": this.payment_method.telebirr_app_id,
// //             "pos_session": this.pos.pos_session.config_id[0],
// //             "traceNo": trace_no,
// //             "amount": order.selected_paymentline.amount,
// //             "phone": '251910493259'
// //         }
// //        console.log("PAYERRRR")
// //        console.log(this.payment_method)
     
        
// //        let info_data= await this._call_telebirr(data);
// //        console.log("IIIIIIIIIIIIIII",info_data.msg)
// //        return self._telebirr_handle_response(info_data);

// //     }

//   }