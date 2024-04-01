/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreenPaymentLines } from "@point_of_sale/app/screens/payment_screen/payment_lines/payment_lines";
import { jsonrpc } from "@web/core/network/rpc_service";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";

patch(PaymentScreenPaymentLines.prototype, {

    setup() {
        super.setup(...arguments);

        this.ui = useState(useService("ui"));
        this.popup = useService("popup");
        this.pos = usePos();

        this.currentOrder = this.pos.get_order();
        this.orderUiState = this.currentOrder.uiState.PaymentScreen
        this.orderUiState.Phone = this.orderUiState.Phone

    }

    // setup() {
    //     super.setup(...arguments);
    //     console.log("LOADED PaymentScreenPaymentLines");
    // },
    // setup() {
    //     super.setup(...arguments);
    //     this.pos = usePos();

    //     this.ui = useState(useService("ui"));
    //     this.currentOrder = this.pos.get_order();
    //     this.orderUiState = this.currentOrder.uiState.ProductScreen
    //     this.orderUiState.Phone = this.orderUiState.Phone

    // },
    // selectPaymentLine(cid) {
    //     updateSelectedPaymentline
    //     console.log("iiiiiiiiiii")
    //     console.log("phoneeee", this.orderUiState.Phone)
    //     const line = this.paymentLines.find((line) => line.cid === cid);
    //     this.currentOrder.select_paymentline(line);
    //     this.numberBuffer.reset();

    // }
  

//     async checkPaymentStatus(){
//         // let data = {
//         //     id:this.payment_method.id,
//         //     pos_ses:pos_ses
//         // }
//         line.set_payment_status('waitingClard')
// console.log("L::::::::::::",line)
//             let response =  await jsonrpc(`/find_pay_confirmed_telebirr`);
//             console.log("Response888888888888888:", response.msg); // Log the entire response object
            
//            return  response.msg
//     }






});