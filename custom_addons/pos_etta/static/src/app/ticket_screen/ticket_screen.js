/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

patch(TicketScreen.prototype, {
    _getToRefundDetail(orderline) {
        let result = super._getToRefundDetail(orderline);
        result.service_charge = orderline.service_charge;
        return result;
    },
    _getSearchFields() {
        var res = super._getSearchFields();
        res.FS_NUMBER = {
            repr: (order) => order.fs_no,
            displayName: _t("FS No"),
            modelField: "fs_no",
        };

        res.RF_NUMBER = {
            repr: (order) => order.rf_no,
            displayName: _t("RF No"),
            modelField: "rf_no",
        };

        return res;
    },
    async onDeleteOrder(order) {
        console.dir(order);
        if (order.rf_no !== "" || order.fs_no !== "") {
            this.env.services.notification.add("Can not delete order which has printed fiscal receipt", {
                type: 'info',
                sticky: false,
                timeout: 10000,
            });
        }
        else {
            if (this.pos.hasAccess(this.pos.config['allow_quantity_change_and_remove_orderline'])) {
                await this.pos.doAuthFirst('allow_quantity_change_and_remove_orderline', 'allow_quantity_change_and_remove_orderline_pin_lock_enabled', 'quantity_change_and_remove', async () => {
                    await super.onDeleteOrder(...arguments);
                });
            }
            else {
                this.env.services.notification.add("You do not have access to delete an order!", {
                    type: 'info',
                    sticky: false,
                    timeout: 10000,
                });
            }
        }
    },
    async toggleStatus(order) {
        if (!order.checked) {
            const { confirmed } = await this.popup.add(ConfirmPopup, {
                title: _t("Confirm Cash Collection"),
                body: _t("Are you sure you have collected %s for %s", this.getTotal(order), order.name),
            });
            if (confirmed) {
                try {
                    let result = await this.orm.call("pos.order", "set_order_checked", [order.name]);
                    if (result) {
                        order.checked = true;
                        this.env.services.notification.add("Order Status Changed", {
                            type: 'info',
                            sticky: false,
                            timeout: 10000,
                        });
                    }
                    else {
                        this.env.services.notification.add("Order Status Change Failed. Please Try Again", {
                            type: 'danger',
                            sticky: false,
                            timeout: 10000,
                        });
                    }
                }
                catch (error) {
                    this.env.services.notification.add(error, {
                        type: 'danger',
                        sticky: false,
                        timeout: 10000,
                    });
                }
            }
        }
    },
    _prepareRefundOrderlineOptions(toRefundDetail) {
        const { qty, orderline } = toRefundDetail;
        const draftPackLotLines = orderline.pack_lot_lines
            ? { modifiedPackLotLines: [], newPackLotLines: orderline.pack_lot_lines }
            : false;

        var res = {
            quantity: -qty,
            price: orderline.price,
            extras: { price_type: "automatic" },
            merge: false,
            refunded_orderline_id: orderline.id,
            tax_ids: orderline.tax_ids,
            discount: orderline.discount,
            service_charge: orderline.service_charge,
            draftPackLotLines: draftPackLotLines,
        };
        return res;
    },
    async onDoRefund() {
        let selectedApprover = await this.selectApproverCashier();
        if (selectedApprover) {
            this.pos.set_is_refund_order(true);
            super.onDoRefund();
        }
    },
    async checkPin(employee) {
        const { confirmed, payload: inputPin } = await this.popup.add(NumberPopup, {
            isPassword: true,
            title: _t("Password?"),
        });

        if (!confirmed) {
            return false;
        }

        if (employee.pin !== Sha1.hash(inputPin)) {
            await this.popup.add(ErrorPopup, {
                title: _t("Incorrect Password"),
                body: _t("Please try again."),
            });
            return false;
        }
        return true;
    },
    async selectApproverCashier() {
        if (this.pos.config.module_pos_hr) {
            const employeesList = this.pos.employees
                .filter((employee) => employee.role === 'manager')
                .map((employee) => {
                    return {
                        id: employee.id,
                        item: employee,
                        label: employee.name,
                        isSelected: false,
                    };
                });
            if (!employeesList.length) {
                this.env.services.notification.add("Not Configured for Refund Mode", {
                    type: 'info',
                    sticky: false,
                    timeout: 10000,
                });
                return undefined;
            }
            const { confirmed, payload: employee } = await this.popup.add(SelectionPopup, {
                title: _t("Select Refund Approver"),
                list: employeesList,
            });

            if (!confirmed || !employee || (employee.pin && !(await this.checkPin(employee)))) {
                return false;
            }

            return true;
        }
        else {
            this.env.services.notification.add("Not Configured for Refund Mode", {
                type: 'info',
                sticky: false,
                timeout: 10000,
            });
        }
    }
});