/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ConnectionLostError } from "@web/core/network/rpc_service";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
    isFiscalPrinted() {
        if (this.currentOrder.is_refund && this.currentOrder.rf_no !== "") {
            return true;
        }

        if (!this.currentOrder.is_refund && this.currentOrder.fs_no !== "") {
            return true;
        }

        return false;
    },
    async _finalizeValidation() {
        if (this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) {
            if (window.Android != undefined) {
                if (window.Android.isAndroidPOS()) {
                    window.Android.openCashDrawer();
                }
            }
            this.hardwareProxy.openCashbox();
        }

        this.currentOrder.date_order = luxon.DateTime.now();
        for (const line of this.paymentLines) {
            if (!line.amount === 0) {
                this.currentOrder.remove_paymentline(line);
            }
        }

        //TODO : printing of fiscal receipt done here
        var fiscalPrintResult = await this.currentOrder.printFiscalReceipt();

        if (fiscalPrintResult || this.isFiscalPrinted()) {
            this.currentOrder.finalized = true;

            // 1. Save order to server.
            this.env.services.ui.block();
            const syncOrderResult = await this.pos.push_single_order(this.currentOrder);
            this.env.services.ui.unblock();

            if (syncOrderResult instanceof ConnectionLostError) {
                this.pos.showScreen(this.nextScreen);
                return;
            } else if (!syncOrderResult) {
                return;
            }

            try {
                // 2. Invoice.
                if (this.shouldDownloadInvoice() && this.currentOrder.is_to_invoice()) {
                    if (syncOrderResult[0]?.account_move) {
                        await this.report.doAction("account.account_invoices", [
                            syncOrderResult[0].account_move,
                        ]);
                    } else {
                        throw {
                            code: 401,
                            message: "Backend Invoice",
                            data: { order: this.currentOrder },
                        };
                    }
                }
            } catch (error) {
                if (error instanceof ConnectionLostError) {
                    Promise.reject(error);
                    return error;
                } else {
                    throw error;
                }
            }

            // 3. Post process.
            if (
                syncOrderResult &&
                syncOrderResult.length > 0 &&
                this.currentOrder.wait_for_push_order()
            ) {
                await this.postPushOrderResolve(syncOrderResult.map((res) => res.id));
            }

            await this.afterOrderValidation(!!syncOrderResult && syncOrderResult.length > 0);
        }
        else {

        }
    }
});

patch(ProductScreen.prototype, {
    async _setValue(val) {
        var newQty = this.numberBuffer.get() ? parseFloat(this.numberBuffer.get()) : 0;
        var orderLines = !!this.currentOrder ? this.currentOrder.get_orderlines() : undefined;
        if (orderLines !== undefined && orderLines.length > 0) {
            var currentOrderLine = this.currentOrder.get_selected_orderline();
            var currentQty = this.currentOrder.get_selected_orderline().get_quantity();
            if (currentOrderLine && this.pos.numpadMode === 'quantity' && newQty < currentQty && !this.pos.hasAccess(this.pos.config['allow_quantity_change_and_remove_orderline'])) {
                this.env.services.notification.add("You do not have access to decrease the quantity of an order line!", {
                    type: 'danger',
                    sticky: false,
                    timeout: 10000,
                });
            } else if (currentOrderLine && this.pos.numpadMode === 'quantity' && val === 'remove' && !this.pos.hasAccess(this.pos.config['allow_quantity_change_and_remove_orderline'])) {
                this.env.services.notification.add("You do not have access to delete an order line!", {
                    type: 'danger',
                    sticky: false,
                    timeout: 10000,
                });
            } else {
                await this.pos.doAuthFirst('allow_quantity_change_and_remove_orderline', 'allow_quantity_change_and_remove_orderline_pin_lock_enabled', 'quantity_change_and_remove', async () => {
                    await super._setValue(val);
                });
            }
        } else {
            super._setValue(val)
        }
    },
    async onNumpadClick(buttonValue) {
        if (buttonValue === 'price') {
            if (this.pos.hasAccess(this.pos.config['allow_price_change'])) {
                await this.pos.doAuthFirst('allow_price_change', 'price_change_pin_lock_enabled', 'price_change', async () => {
                    super.onNumpadClick(buttonValue);
                });
            }
            else {
                this.pos.env.services.popup.add(ErrorPopup, {
                    title: _t('Access Denied'),
                    body: _t('You do not have access to change price!'),
                });
            }
        } else if (buttonValue === 'discount' && this.pos.get_cashier().role !== 'manager') {
            this.pos.env.services.popup.add(ErrorPopup, {
                title: _t('Access Denied'),
                body: _t('You do not have access to apply discount!'),
            });
        } else {
            super.onNumpadClick(buttonValue);
        }
    }
});

patch(ActionpadWidget.prototype, {
    setup() {
        this.popup = useService("popup");
        super.setup();
    },
    async submitOrder() {
        let self = this;
        const { confirmed } = await this.popup.add(ConfirmPopup, {
            title: _t("Confirm Order"),
            body: _t("Are you sure want to make this order?"),
        });
        if (confirmed) {
            let bad_order = false;
            let product_names = '';
            this.pos.get_order().orderlines.forEach(line => {
                if (line.get_display_price() == 0.00 || line.price < 0.00) {
                    bad_order = true;
                    product_names += '-' + line.product.display_name + "\n"
                }
            });

            if (bad_order) {
                if (product_names) {
                    self.env.services.popup.add(ErrorPopup, {
                        'title': _t("Product With 0 Price"),
                        'body': _t('You are not allowed to have the zero prices on the order line.\n %s', product_names),
                    });
                    return;
                }
            }

            await super.submitOrder();
    
        }
        else {
            console.log("Not ordered");
        }
    }
});