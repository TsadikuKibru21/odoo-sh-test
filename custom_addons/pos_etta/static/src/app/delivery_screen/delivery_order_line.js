/** @odoo-module */

import { Component } from "@odoo/owl";

export class DeliveryOrderLine extends Component {
    static template = "pos_etta.DeliveryOrderLine";

    get highlight() {
        return this._isOrderSelected ? "highlight active" : "";
    }

    get _isOrderSelected() {
        return this.props.order === this.props.selectedorder;
    }

    handleOrderLineClick(event) {

        this.props.clickOrderLineEtta(event);
    }

    handleonClickCartButton(event) {

        this.props.onClickCartButton(event);
    }

}
