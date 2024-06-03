/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";

patch(Navbar.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },

    showCashier() {
        const currentScreen = this.pos.mainScreen.component;
        console.log("CURRENT SCREEN ",currentScreen)
        return !(currentScreen === ProductScreen || currentScreen === TicketScreen);
    }
});
