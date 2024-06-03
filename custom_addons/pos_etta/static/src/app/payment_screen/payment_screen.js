/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ConnectionLostError } from "@web/core/network/rpc_service";

patch(PaymentScreen.prototype, {
    isFiscalPrinted() {
        // console.log("=== currentOrder ===");
        // console.log(this.currentOrder);
        if (this.currentOrder.is_refund && this.currentOrder.rf_no !== "") {
            return true;
        }

        if (!this.currentOrder.is_refund && this.currentOrder.fs_no !== "") {
            return true;
        }

        return false;
    },   
    // async _finalizeValidation() {
    //     if (this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) {
    //         if (window.Android != undefined) {
    //             if (window.Android.isAndroidPOS()) {
    //                 window.Android.openCashDrawer();
    //             }
    //         }
    //         this.hardwareProxy.openCashbox();
    //     }

    //     this.currentOrder.date_order = luxon.DateTime.now();
    //     for (const line of this.paymentLines) {
    //         if (!line.amount === 0) {
    //             this.currentOrder.remove_paymentline(line);
    //         }
    //     }

    //     //TODO : printing of fiscal receipt done here
    //     var fiscalPrintResult = await this.currentOrder.printFiscalReceipt();

    //     if (fiscalPrintResult || this.isFiscalPrinted()) {
    //         this.currentOrder.finalized = true;

    //         // 1. Save order to server.
    //         this.env.services.ui.block();
    //         const syncOrderResult = await this.pos.push_single_order(this.currentOrder);
    //         this.env.services.ui.unblock();

    //         if (syncOrderResult instanceof ConnectionLostError) {
    //             this.pos.showScreen(this.nextScreen);
    //             return;
    //         } else if (!syncOrderResult) {
    //             return;
    //         }

    //         try {
    //             // 2. Invoice.
    //             if (this.shouldDownloadInvoice() && this.currentOrder.is_to_invoice()) {
    //                 if (syncOrderResult[0]?.account_move) {
    //                     await this.report.doAction("account.account_invoices", [
    //                         syncOrderResult[0].account_move,
    //                     ]);
    //                 } else {
    //                     throw {
    //                         code: 401,
    //                         message: "Backend Invoice",
    //                         data: { order: this.currentOrder },
    //                     };
    //                 }
    //             }
    //         } catch (error) {
    //             if (error instanceof ConnectionLostError) {
    //                 Promise.reject(error);
    //                 return error;
    //             } else {
    //                 throw error;
    //             }
    //         }

    //         // 3. Post process.
    //         if (
    //             syncOrderResult &&
    //             syncOrderResult.length > 0 &&
    //             this.currentOrder.wait_for_push_order()
    //         ) {
    //             await this.postPushOrderResolve(syncOrderResult.map((res) => res.id));
    //         }

    //         await this.afterOrderValidation(!!syncOrderResult && syncOrderResult.length > 0);
    //     }
    //     else {

    //     }
    // }
});