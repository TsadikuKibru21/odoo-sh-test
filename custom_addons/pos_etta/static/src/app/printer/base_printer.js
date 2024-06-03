/** @odoo-module */

import { BasePrinter } from "@point_of_sale/app/printer/base_printer";
import { patch } from "@web/core/utils/patch";

patch(BasePrinter.prototype, {
    setup(params) {
        super.setup(...arguments);
        const { rpc, url } = params;
        this.rpc = rpc;
        this.url = url;
    },
    async printReceipt(receipt, printer) {
        if (receipt) {
            this.receiptQueue.push(receipt);
        }
        let escposReceipt, printResult;
        while (this.receiptQueue.length > 0) {
            receipt = this.receiptQueue.shift();
            let escposReceipt = this.generateKitchenOrderReceipt(receipt, printer);
            try {
                let merged = {
                    printer: printer,
                    receipt: escposReceipt
                };

                // console.log("TO BE SENT TO THERMAL PRINTER");
                // console.log(merged);

                if (window.Android.isAndroidPOS()) {

                    window.handleOrderPrintResponse = function(response) {
                        // console.log(JSON.parse(response));
                    }
                    
                    var result = window.Android.printTcp(JSON.stringify(merged));

                    var responseObject = JSON.parse(result);
                    
                    // console.log(responseObject);
                }
                else {
                    this.env.services.notification.add("Invalid Device", {
                        type: 'danger',
                        sticky: false,
                        timeout: 10000,
                    });
                }
            } catch {
                // Error in communicating to the IoT box.
                this.receiptQueue.length = 0;
                return this.getActionError();
            }
            // rpc call is okay but printing failed because
            // IoT box can't find a printer.
            if (!printResult || printResult.result === false) {
                this.receiptQueue.length = 0;
                return this.getResultsError(printResult);
            }
        }
        return { successful: true };
    },
    sendPrintingOrder(receipt, printer) {
        return this.rpc(`${this.url}/orderpinter/printorder`, { receipt, printer });
    },
    generateKitchenOrderReceipt(orderData, printer) {
        let receiptText = "\x1B\x40";
        receiptText += "\x1B\x21\x1C"; // Set font size to double width and double height
        receiptText += "[C]" + printer.name + "\n";
        receiptText += "\x1B\x21\x00"; // Reset font size
        receiptText += "------------------------------------------------\n";
    
        receiptText += "[L]<b>Table:</b> " + orderData.table_name + "\n";
        receiptText += "[L]<b>Floor:</b> " + orderData.floor_name + "\n";
        receiptText += "[L]<b>Order Number:</b> " + orderData.name + "\n";
        receiptText += "[L]<b>Cashier:</b> " + orderData.cashier + "\n";
        receiptText += "[L]<b>Date:</b> " + orderData.date + "\n";
        receiptText += "[L]<b>Time:</b> " + orderData.time.hours + ":" + orderData.time.minutes + "\n";
    
        if (orderData.new != undefined && orderData.new && orderData.new.length > 0) {
            receiptText += "------------------------------------------------\n";
            receiptText += "[L]<b>NEW ITEMS:</b>\n";
            orderData.new.forEach(item => {
                receiptText += "[L]" + item.name + " x " + item.quantity + "\n";
            });
        }
    
        if (orderData.cancelled != undefined && orderData.cancelled && orderData.cancelled.length > 0) {
            receiptText += "------------------------------------------------\n";
            receiptText += "[L]<b>CANCELLED ITEMS:</b>\n";
            orderData.cancelled.forEach(item => {
                receiptText += "[L]" + item.name + " x " + item.quantity + "\n";
            });
        }
    
        receiptText += "\n\n\n";
        receiptText += "[L]\n";
        receiptText +="[L]\n";
    
        return receiptText;
    }
});
