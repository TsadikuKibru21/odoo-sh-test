/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(OrderWidget.prototype, {

    setup() {
        super.setup();
        this.pos = usePos();
    },
    voidOrders() {
        var result = [];
        var VOIDED_ORDERS = localStorage.getItem('VOIDED_ORDERS');
        
        if(VOIDED_ORDERS != undefined){
            var parsedData = JSON.parse(VOIDED_ORDERS);
            VOIDED_ORDERS = parsedData.filter(item => item.name === this.pos.get_order().name);
            VOIDED_ORDERS.forEach(function (order) {
                const dataToStore = {
                    name: order.name,
                    productName: order.productName,
                    unitPrice: order.unitPrice,
                    quantity: order.quantity,
                };
                result.push(dataToStore);
            });
        }
        
        return result;
    }

});