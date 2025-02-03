/** @odoo-module **/

import paymentForm from '@payment/js/payment_form';
import paymentButton from '@payment/js/payment_button';
import { _t } from '@web/core/l10n/translation';

import { jsonrpc } from "@web/core/network/rpc_service";
console.log("Custom payment form script loaded.");
// window.location.href = '/payment/custom_status?status=processing'; // Update this URL as needed

paymentForm.include({

    //   /**
    //   * Create an event listener for the payment button located outside the payment form.
    //   * @override
    //  */
    // async start() {
    //     const submitButton = document.querySelector('[name="o_payment_submit_button"]');
    //     submitButton.addEventListener('click', ev => this._submitForm(ev));
    //     console.log("********************* onclick **************")
       
    //     return await this._super(...arguments);
    // },
    async _submitForm(ev) {
        console.log("********************* onclick **************")
        var customerPhoneNumber = $('#telebirr_phone').val();
        console.log(customerPhoneNumber)
        const phoneNumberRegex = /^9\d{8}$/; // Matches a 9-digit number starting with '9'
        if (!phoneNumberRegex.test(customerPhoneNumber)) {
            this._displayErrorDialog(
                _t("Phone number must be 9 digits and start with 9.")
            );
            return;
        }
        if (customerPhoneNumber == "") {
            this._displayErrorDialog(
                _t("Please Enter Phone number")
            );
            return;
        }
       const a= await jsonrpc(
            '/payment/telebirr/update_phone',
            {
                'phone_number': customerPhoneNumber
            }
        )
        console.log(a)
        ev.stopPropagation();
        ev.preventDefault();
        console.log("**************************************************")
        
        const checkedRadio = this.el.querySelector('input[name="o_payment_radio"]:checked');

        // Block the entire UI to prevent fiddling with other widgets.
        this._disableButton(true);

        // Initiate the payment flow of the selected payment option.
        const flow = this.paymentContext.flow = this._getPaymentFlow(checkedRadio);
        const paymentOptionId = this.paymentContext.paymentOptionId = this._getPaymentOptionId(
            checkedRadio
        );
        if (flow === 'token' && this.paymentContext['assignTokenRoute']) { // Assign token flow.
            await this._assignToken(paymentOptionId);
        } else { // Both tokens and payment methods must process a payment operation.
            const providerCode = this.paymentContext.providerCode = this._getProviderCode(
                checkedRadio
            );
            const pmCode = this.paymentContext.paymentMethodCode = this._getPaymentMethodCode(
                checkedRadio
            );
            this.paymentContext.providerId = this._getProviderId(checkedRadio);
            if (this._getPaymentOptionType(checkedRadio) === 'token') {
                this.paymentContext.tokenId = paymentOptionId;
            } else { // 'payment_method'
                this.paymentContext.paymentMethodId = paymentOptionId;
            }
            const inlineForm = this._getInlineForm(checkedRadio);
            this.paymentContext.tokenizationRequested = inlineForm?.querySelector(
                '[name="o_payment_tokenize_checkbox"]'
            )?.checked ?? this.paymentContext['mode'] === 'validation';
            await this._initiatePaymentFlow(providerCode, paymentOptionId, pmCode, flow);
        }
    },

    // /**
    //  * Override the payment action to redirect to a custom page.
    //  */
    // payEvent: function (ev) {
    //     ev.preventDefault();
    //     console.log("Pay button clicked. Redirecting to custom page...");

    //     // Redirect to your custom page
    //     window.location.href = '/payment/custom_status?status=processing'; // Update this URL as needed
    // },
    

     async _initiatePaymentFlow(providerCode, paymentOptionId, paymentMethodCode, flow) {

       
             console.log("############################# custom _initiatePaymentFlow ############")
            // Create a transaction and retrieve its processing values.
            console.log("##################### initate payment ########")
          
            this.rpc(
                this.paymentContext['transactionRoute'],
                this._prepareTransactionRouteParams(),
            ).then(processingValues => {
                if (flow === 'redirect') {
                    this._processRedirectFlow(
                        providerCode, paymentOptionId, paymentMethodCode, processingValues
                    );
                    console.log("################################## customerPhoneNumber ")
                    console.log(processingValues)

                    
                    if(paymentMethodCode=='telebirr'){
                        
                        window.location.href = '/payment/custom_status';
                    }
                    console.log("################################## customerPhoneNumber ")
                    console.log(processingValues)
                
                } else if (flow === 'direct') {
                    this._processDirectFlow(
                        providerCode, paymentOptionId, paymentMethodCode, processingValues
                    );
                    if(paymentMethodCode=='telebirr'){
                        window.location.href = '/payment/custom_status';
                    }
                } else if (flow === 'token') {
                    this._processTokenFlow(
                        providerCode, paymentOptionId, paymentMethodCode, processingValues
                    );
                    if(paymentMethodCode=='telebirr'){
                        window.location.href = '/payment/custom_status';
                    }
                }
                console.log("################################## customerPhoneNumber ")
                console.log(processingValues)
                
            }).catch(error => {
                if (error instanceof RPCError) {
                    this._displayErrorDialog(_t("Payment processing failed"), error.data.message);
                    this._enableButton(); // The button has been disabled before initiating the flow.
                } else {
                    return Promise.reject(error);
                }
            });
        },

      
});



paymentButton.include({

    // /**
    //  * Verify that the payment button is ready to be enabled.
    //  *
    //  * The conditions are that:
    //  * - a delivery carrier is selected and ready (the price is computed) if deliveries are enabled;
    //  * - the "Terms and Conditions" checkbox is ticked if it is present.
    //  *
    //  * @override from @payment/js/payment_button
    //  * @return {boolean}
    //  */
    // _canSubmit() {
    //     console.log("Custom payment submit.");
    //     console.log(this)
    //     // window.location.href = '/payment/custom_status?status=success';
    //     return this._super(...arguments)
    // },

   
});
