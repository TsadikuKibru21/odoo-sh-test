/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { FloorScreen } from "@pos_restaurant/app/floor_screen/floor_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";

patch(FloorScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },

    async onSelectTable(table, ev) {
       

        const waiterNames = [];

        for (let i = 0; i < table.waiter_ids.length; i++) {
            const tableId = table.waiter_ids[i];
            const employee = this.pos.employees.find(emp => emp.id === tableId);
            console.log(employee)
            if (employee)
            {
                waiterNames.push(employee.name); 
            } 
            else {
                console.log(`Employee not found for table ID: ${tableId}`);
            }
        }
        

        if (this.pos.isEditMode) {
            if (ev.ctrlKey || ev.metaKey) {
                this.state.selectedTableIds.push(table.id);
            } else {
                this.state.selectedTableIds = [];
                this.state.selectedTableIds.push(table.id);
            }
        } else {
            const cashier = this.pos.get_cashier().name;
            if(this.pos.config.allow_waiter_reservation){
            if (waiterNames.includes(cashier)) {
                if (this.pos.orderToTransfer && table.order_count > 0) {
                    const { confirmed } = await this.popup.add(ConfirmPopup, {
                        title: _t("Table is not empty"),
                        body: _t(
                            "The table already contains an order. Do you want to proceed and transfer the order here?"
                        ),
                        confirmText: _t("Yes"),
                    });
                    if (!confirmed) {
                        table = this.pos.tables_by_id[this.pos.orderToTransfer.tableId];
                        this.pos.orderToTransfer = null;
                    }
                }
                if (this.pos.orderToTransfer) {
                    await this.pos.transferTable(table);
                } else {
                    try {
                        await this.pos.setTable(table);
                    } catch (e) {
                        if (!(e instanceof ConnectionLostError)) {
                            throw e;
                        }
                        Promise.reject(e);
                    }
                }
                const order = this.pos.get_order();
                this.pos.showScreen(order.get_screen_data().name);
            }
            else {
                console.log("FALSSEEEE")
                this.env.services.notification.add("This table is already reserved.", {
                    type: 'danger',
                    sticky: false,
                    timeout: 10000,
                });
            }}
            else{
                if (this.pos.orderToTransfer && table.order_count > 0) {
                    const { confirmed } = await this.popup.add(ConfirmPopup, {
                        title: _t("Table is not empty"),
                        body: _t(
                            "The table already contains an order. Do you want to proceed and transfer the order here?"
                        ),
                        confirmText: _t("Yes"),
                    });
                    if (!confirmed) {
                        table = this.pos.tables_by_id[this.pos.orderToTransfer.tableId];
                        this.pos.orderToTransfer = null;
                    }
                }
                if (this.pos.orderToTransfer) {
                    await this.pos.transferTable(table);
                } else {
                    try {
                        await this.pos.setTable(table);
                    } catch (e) {
                        if (!(e instanceof ConnectionLostError)) {
                            throw e;
                        }
                        Promise.reject(e);
                    }
                }
                const order = this.pos.get_order();
                this.pos.showScreen(order.get_screen_data().name);
            }
        }
    }
});