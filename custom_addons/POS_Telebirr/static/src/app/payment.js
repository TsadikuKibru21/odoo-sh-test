/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { sprintf } from "@web/core/utils/strings";
const { DateTime } = luxon;

export class PaymentTelebirr extends PaymentInterface {
    setup() {
        super.setup(...arguments);
        this.paymentLineResolvers = {};
    }

    send_payment_request(cid) {
        super.send_payment_request(cid);
        return this._adyen_pay(cid);
    }}