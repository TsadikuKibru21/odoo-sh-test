/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";
patch(TicketScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },
    getFilteredOrderList() {
     
        if (this._state.ui.filter == "SYNCED") {
            return this._state.syncedOrders.toShow;
        }
        const filterCheck = (order) => {
            if (this._state.ui.filter && this._state.ui.filter !== "ACTIVE_ORDERS") {
                const screen = order.get_screen_data();
                return this._state.ui.filter === this._getScreenToStatusMap()[screen.name];
            }
            if(this.pos.config.allow_waiter_reservation){


           return order.cashier.name===this.pos.get_cashier().name;}
           else{
            return true
           }
        };
        const { fieldName, searchTerm } = this._state.ui.searchDetails;
        const searchField = this._getSearchFields()[fieldName];
        const searchCheck = (order) => {
            if (!searchField) {
                return true;
            }
            const repr = searchField.repr(order);
            if (repr === null) {
                return true;
            }
            if (!searchTerm) {
                return true;
            }
            return repr && repr.toString().toLowerCase().includes(searchTerm.toLowerCase());
        };
        const predicate = (order) => {
            return filterCheck(order) && searchCheck(order);
        };
        return this._getOrderList().filter(predicate);
    }
});
